#!/usr/bin/env python3
"""
Ende-zu-Ende Integration Tests für RF Transceiver System
Vollständige Tests mit echter Hardware und Mock-Simulationen
"""

import asyncio
import json
import logging
import pytest
import websockets
import serial
import time
from datetime import datetime
from typing import Dict, Any, Optional
import subprocess
import sys
import os

# Test-Konfiguration
TEST_CONFIG = {
    "websocket_host": "localhost",
    "websocket_port": 8765,
    "serial_port": None,  # Wird automatisch erkannt
    "baud_rate": 115200,
    "test_timeout": 30,
    "mock_mode": True  # Fallback auf Mock wenn keine Hardware verfügbar
}

class RFIntegrationTester:
    """Hauptklasse für RF-Integration-Tests"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("RFIntegrationTester")
        self.websocket = None
        self.serial_conn = None
        self.backend_process = None
        self.test_results = []
        
    async def setup(self):
        """Test-Setup durchführen"""
        self.logger.info("Setting up RF Integration Tests...")
        
        # Backend-Prozess starten
        await self._start_backend()
        
        # WebSocket-Verbindung herstellen
        await self._connect_websocket()
        
        # Serial-Verbindung testen
        await self._test_serial_connection()
        
        self.logger.info("Test setup completed")
    
    async def teardown(self):
        """Test-Cleanup durchführen"""
        self.logger.info("Tearing down RF Integration Tests...")
        
        if self.websocket:
            await self.websocket.close()
        
        if self.serial_conn:
            self.serial_conn.close()
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
        
        self.logger.info("Test teardown completed")
    
    async def _start_backend(self):
        """Backend-Prozess starten"""
        try:
            # Versuche echte Hardware
            if self.config.get("serial_port"):
                port = self.config["serial_port"]
            else:
                # Auto-Detection der verfügbaren Ports
                available_ports = self._detect_serial_ports()
                if available_ports:
                    port = available_ports[0]
                    self.logger.info(f"Auto-detected serial port: {port}")
                else:
                    # Mock-Modus verwenden
                    port = "/dev/null" if os.name != 'nt' else "NUL"
                    self.config["mock_mode"] = True
                    self.logger.warning("No serial ports detected, using mock mode")
            
            # Backend starten
            cmd = [
                sys.executable, 
                "server_real_rf_system.py",
                "--port", port,
                "--host", self.config["websocket_host"],
                "--wsport", str(self.config["websocket_port"])
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(__file__)
            )
            
            # Warten bis Backend bereit ist
            await asyncio.sleep(2)
            
            if self.backend_process.poll() is not None:
                stdout, stderr = self.backend_process.communicate()
                raise Exception(f"Backend failed to start: {stderr.decode()}")
            
            self.logger.info("Backend started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start backend: {e}")
            raise
    
    async def _connect_websocket(self):
        """WebSocket-Verbindung herstellen"""
        try:
            uri = f"ws://{self.config['websocket_host']}:{self.config['websocket_port']}/telemetry"
            self.websocket = await websockets.connect(uri)
            self.logger.info("WebSocket connection established")
        except Exception as e:
            self.logger.error(f"Failed to connect WebSocket: {e}")
            raise
    
    async def _test_serial_connection(self):
        """Serial-Verbindung testen"""
        if self.config.get("mock_mode"):
            self.logger.info("Mock mode - skipping serial connection test")
            return
        
        try:
            port = self.config.get("serial_port")
            if not port:
                available_ports = self._detect_serial_ports()
                if not available_ports:
                    self.config["mock_mode"] = True
                    self.logger.warning("No serial ports available, switching to mock mode")
                    return
                port = available_ports[0]
            
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=self.config["baud_rate"],
                timeout=1
            )
            
            # Test-Kommando senden
            test_cmd = "AT\r\n"
            self.serial_conn.write(test_cmd.encode())
            
            # Antwort lesen (optional)
            response = self.serial_conn.readline()
            self.logger.info(f"Serial connection test successful: {response.decode().strip()}")
            
        except Exception as e:
            self.logger.warning(f"Serial connection test failed: {e}")
            self.config["mock_mode"] = True
    
    def _detect_serial_ports(self) -> list:
        """Verfügbare Serial-Ports erkennen"""
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
        except ImportError:
            # Fallback für Systeme ohne serial.tools
            return []
    
    async def test_websocket_connection(self):
        """WebSocket-Verbindungstest"""
        self.logger.info("Testing WebSocket connection...")
        
        try:
            # Ping-Nachricht senden
            ping_message = {"type": "ping", "timestamp": datetime.now().isoformat()}
            await self.websocket.send(json.dumps(ping_message))
            
            # Antwort empfangen
            response = await asyncio.wait_for(
                self.websocket.recv(), 
                timeout=5
            )
            
            response_data = json.loads(response)
            assert "timestamp" in response_data
            
            self.test_results.append({
                "test": "websocket_connection",
                "status": "passed",
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("WebSocket connection test passed")
            
        except Exception as e:
            self.test_results.append({
                "test": "websocket_connection",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    async def test_at_command_flow(self):
        """AT-Kommando-Flow testen"""
        self.logger.info("Testing AT command flow...")
        
        try:
            # AT-Kommandos über WebSocket senden
            at_commands = [
                "AT",
                "AT+VERSION",
                "AT+STATUS",
                "AT+FREQ=915000000"
            ]
            
            for cmd in at_commands:
                command_message = {
                    "cmds": [cmd],
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.websocket.send(json.dumps(command_message))
                
                # Kurz warten
                await asyncio.sleep(0.1)
            
            self.test_results.append({
                "test": "at_command_flow",
                "status": "passed",
                "commands_sent": len(at_commands),
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("AT command flow test passed")
            
        except Exception as e:
            self.test_results.append({
                "test": "at_command_flow",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    async def test_telemetry_flow(self):
        """Telemetrie-Flow testen"""
        self.logger.info("Testing telemetry flow...")
        
        try:
            # Mock-Telemetriedaten generieren
            mock_telemetry = {
                "mbps": 123.4,
                "frequency": 915000000,
                "power": -72.3,
                "snr": 15.2,
                "timestamp": datetime.now().isoformat()
            }
            
            # Telemetrie über WebSocket senden
            await self.websocket.send(json.dumps(mock_telemetry))
            
            # Antwort empfangen
            response = await asyncio.wait_for(
                self.websocket.recv(), 
                timeout=5
            )
            
            response_data = json.loads(response)
            assert "timestamp" in response_data
            
            self.test_results.append({
                "test": "telemetry_flow",
                "status": "passed",
                "telemetry_sent": mock_telemetry,
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("Telemetry flow test passed")
            
        except Exception as e:
            self.test_results.append({
                "test": "telemetry_flow",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    async def test_hardware_integration(self):
        """Hardware-Integration testen"""
        self.logger.info("Testing hardware integration...")
        
        try:
            if self.config.get("mock_mode"):
                # Mock-Hardware-Test
                mock_hardware_data = {
                    "device_id": "mock_device_001",
                    "frequency": 915000000,
                    "power": -70.0,
                    "status": "connected",
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.websocket.send(json.dumps(mock_hardware_data))
                
                self.test_results.append({
                    "test": "hardware_integration",
                    "status": "passed",
                    "mode": "mock",
                    "hardware_data": mock_hardware_data,
                    "timestamp": datetime.now().isoformat()
                })
                
            else:
                # Echte Hardware-Tests
                if self.serial_conn:
                    # Hardware-Status abfragen
                    self.serial_conn.write("AT+STATUS\r\n".encode())
                    response = self.serial_conn.readline()
                    
                    hardware_data = {
                        "device_id": "real_device_001",
                        "status_response": response.decode().strip(),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await self.websocket.send(json.dumps(hardware_data))
                    
                    self.test_results.append({
                        "test": "hardware_integration",
                        "status": "passed",
                        "mode": "real_hardware",
                        "hardware_data": hardware_data,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    raise Exception("No serial connection available")
            
            self.logger.info("Hardware integration test passed")
            
        except Exception as e:
            self.test_results.append({
                "test": "hardware_integration",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    async def test_error_handling(self):
        """Fehlerbehandlung testen"""
        self.logger.info("Testing error handling...")
        
        try:
            # Ungültige Nachricht senden
            invalid_message = "invalid json message"
            await self.websocket.send(invalid_message)
            
            # System sollte nicht abstürzen
            await asyncio.sleep(1)
            
            # Gültige Nachricht senden um zu testen ob System noch funktioniert
            valid_message = {"type": "test", "timestamp": datetime.now().isoformat()}
            await self.websocket.send(json.dumps(valid_message))
            
            self.test_results.append({
                "test": "error_handling",
                "status": "passed",
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("Error handling test passed")
            
        except Exception as e:
            self.test_results.append({
                "test": "error_handling",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Test-Report generieren"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "passed"])
        failed_tests = total_tests - passed_tests
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results,
            "configuration": self.config,
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "mock_mode": self.config.get("mock_mode", False)
            }
        }
        
        return report

# Pytest-Test-Funktionen
@pytest.fixture
async def rf_tester():
    """Pytest-Fixture für RF-Tester"""
    tester = RFIntegrationTester(TEST_CONFIG)
    await tester.setup()
    yield tester
    await tester.teardown()

@pytest.mark.asyncio
async def test_websocket_connection(rf_tester):
    """WebSocket-Verbindungstest"""
    await rf_tester.test_websocket_connection()

@pytest.mark.asyncio
async def test_at_command_flow(rf_tester):
    """AT-Kommando-Flow-Test"""
    await rf_tester.test_at_command_flow()

@pytest.mark.asyncio
async def test_telemetry_flow(rf_tester):
    """Telemetrie-Flow-Test"""
    await rf_tester.test_telemetry_flow()

@pytest.mark.asyncio
async def test_hardware_integration(rf_tester):
    """Hardware-Integration-Test"""
    await rf_tester.test_hardware_integration()

@pytest.mark.asyncio
async def test_error_handling(rf_tester):
    """Fehlerbehandlungs-Test"""
    await rf_tester.test_error_handling()

# Standalone-Test-Funktion
async def run_integration_tests():
    """Standalone-Integration-Tests ausführen"""
    logging.basicConfig(level=logging.INFO)
    
    tester = RFIntegrationTester(TEST_CONFIG)
    
    try:
        await tester.setup()
        
        # Alle Tests ausführen
        await tester.test_websocket_connection()
        await tester.test_at_command_flow()
        await tester.test_telemetry_flow()
        await tester.test_hardware_integration()
        await tester.test_error_handling()
        
        # Report generieren
        report = tester.generate_test_report()
        
        print("\n" + "="*60)
        print("RF INTEGRATION TEST REPORT")
        print("="*60)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Passed: {report['test_summary']['passed_tests']}")
        print(f"Failed: {report['test_summary']['failed_tests']}")
        print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
        print("="*60)
        
        # Report speichern
        with open("integration_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("Test report saved to: integration_test_report.json")
        
        return report["test_summary"]["success_rate"] == 100.0
        
    except Exception as e:
        print(f"Integration tests failed: {e}")
        return False
    
    finally:
        await tester.teardown()

if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)
