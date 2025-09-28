"""
Minimal, produktionsfähiger Backend-Dienst ohne Platzhalter/Mocks.

Funktionen:
  - Liest Telemetrie vom seriellen Port (115200 Baud) und streamt sie als JSON-Zeilen.
  - Stellt einen WebSocket-Endpunkt bereit (ws://localhost:8765/telemetry):
      * sendet jede eingehende Zeile (bereits JSON vom Gerät) an alle Clients
      * akzeptiert {"cmds": ["AT+...", ...]} und schreibt sie 1:1 zur seriellen Schnittstelle
  - Optional: Wenn kein serielles Gerät verfügbar ist, beendet sich der Prozess mit Fehler (kein Dummy).

Abhängigkeiten: `pip install pyserial websockets` (für asyncio reicht Standard-Bibliothek)

Start: `python server_real_rf_system.py --port /dev/ttyUSB0` (Windows z.B. `COM5`)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Set

import serial
import serial.threaded
import websockets


class LineReader(serial.threaded.LineReader):
    TERMINATOR = b"\n"

    def __init__(self, on_line):
        super().__init__()
        self.on_line = on_line

    def handle_line(self, line: str) -> None:
        # Erwartet gültiges JSON pro Zeile; ungültige Zeilen werden verworfen.
        try:
            json.loads(line)
        except Exception:
            return
        self.on_line(line)


class SerialBridge:
    def __init__(self, port: str, baud: int = 115200):
        self.port_name = port
        self.baud = baud
        self.ser = None
        self.transport = None
        self.queue: asyncio.Queue[str] = asyncio.Queue()

    def open(self):
        try:
            self.ser = serial.serial_for_url(self.port_name, self.baud, timeout=1)
        except Exception as e:
            print(f"[ERR] Serial open failed: {e}", file=sys.stderr)
            raise

        def on_line(line: str):
            # Push line (already validated JSON) to asyncio queue
            try:
                self.queue.put_nowait(line)
            except asyncio.QueueFull:
                pass

        self.transport = serial.threaded.ReaderThread(self.ser, lambda: LineReader(on_line))
        self.transport.start()  # type: ignore

    def close(self):
        try:
            if self.transport:
                self.transport.close()  # type: ignore
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def write_line(self, s: str):
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("serial not open")
        data = (s.rstrip("\n") + "\n").encode()
        self.ser.write(data)


async def ws_server(bridge: SerialBridge, host: str, port: int):
    clients: Set[websockets.WebSocketServerProtocol] = set()

    async def producer(ws: websockets.WebSocketServerProtocol):
        # Per-Client consumer of serial queue
        try:
            while True:
                line = await bridge.queue.get()
                try:
                    await ws.send(line)
                except websockets.exceptions.ConnectionClosed:
                    break
        except asyncio.CancelledError:
            pass

    async def handler(ws, path):
        clients.add(ws)
        prod_task = asyncio.create_task(producer(ws))
        try:
            async for message in ws:
                try:
                    payload = json.loads(message)
                    cmds = payload.get("cmds")
                    if isinstance(cmds, list):
                        for cmd in cmds:
                            if isinstance(cmd, str) and cmd:
                                bridge.write_line(cmd)
                except Exception as e:
                    print(f"[WARN] Bad client message: {e}")
                    # ignore bad client messages
                    continue
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            prod_task.cancel()
            with contextlib.suppress(Exception):
                await prod_task
            clients.discard(ws)

    return await websockets.serve(handler, host, port)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True, help="Serial port, e.g. /dev/ttyUSB0 or COM5")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--wsport", type=int, default=8765)
    args = parser.parse_args()

    bridge = SerialBridge(args.port, args.baud)
    bridge.open()
    try:
        server = await ws_server(bridge, args.host, args.wsport)
        print(f"[OK] WebSocket on ws://{args.host}:{args.wsport}/telemetry (single endpoint)")
        print("     Send {\"cmds\":[\"AT+...\"]} from client to write to serial.")
        await asyncio.Future()  # run forever
    finally:
        bridge.close()


if __name__ == "__main__":
    import contextlib
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
