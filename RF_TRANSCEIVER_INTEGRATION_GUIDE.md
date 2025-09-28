# RF-Transceiver Integration Guide

## 🎯 Übersicht

Dieses System ermöglicht echte RF-Transceiver-Integration über zwei Wege:
1. **Web Serial** (direkt im Browser - Chrome/Edge)
2. **WebSocket-Bridge** (über Python-Backend - alle Browser)

## 🔧 System-Anforderungen

### Hardware
- RF-Transceiver/Gerät mit serieller Schnittstelle (115200 Baud)
- USB-zu-Serial-Adapter (falls nötig)
- Windows/Linux/Mac-System

### Software
- Python 3.7+ mit Dependencies:
  ```bash
  pip install pyserial websockets
  ```
- Moderne Browser (Chrome/Edge für Web Serial, alle für WebSocket)

## 🚀 Schnellstart

### 1. Verfügbare Ports identifizieren
```bash
python -c "import serial.tools.list_ports; [print(f'{port.device} - {port.description}') for port in serial.tools.list_ports.comports()]"
```

### 2. Backend starten
```bash
# Windows
START_RF_BACKEND.bat COM5

# Linux/Mac
./start_rf_backend.sh /dev/ttyUSB0

# Oder direkt
python server_real_rf_system.py --port COM5 --host 127.0.0.1 --wsport 8765
```

### 3. Frontend öffnen
- React-App starten
- "Connect"-Button klicken
- System wählt automatisch beste Verbindung (Web Serial → WebSocket)

## 📡 Datenformate

### Telemetrie (Gerät → System)
Das Gerät muss JSON-Zeilen über serielle Schnittstelle senden:

```json
{"mbps": 123.4}
{"f": 915000000, "p": -72.3}
{"f": 868.1, "p": -85.2}
```

**Formate:**
- `mbps`: Throughput in Megabit pro Sekunde
- `f`: Frequenz (Hz oder MHz akzeptiert)
- `p`: Leistung in dBm

### Kommandos (System → Gerät)
AT-Kommandos werden automatisch weitergeleitet:

```bash
# Direkt (Web Serial)
AT+QCFG="band",0,0,0x800C0

# Über WebSocket
{"cmds": ["AT+QCFG=\"band\",0,0,0x800C0", "AT+QCFG=\"CA_COMBINATION\",\"B1+B3\""]}
```

## 🔌 Verbindungsarten

### Web Serial (Direkt)
- **Vorteile:** Niedrige Latenz, keine Backend nötig
- **Nachteile:** Nur Chrome/Edge, Benutzer muss Port wählen
- **Verwendung:** Automatisch wenn verfügbar

### WebSocket-Bridge (Backend)
- **Vorteile:** Alle Browser, zentrale Verwaltung
- **Nachteile:** Zusätzlicher Prozess nötig
- **Verwendung:** Automatischer Fallback

## 🛠️ Hardware-Integration

### Vodafone RF Stick
```bash
# Port identifizieren
python -c "import serial.tools.list_ports; ports = [p for p in serial.tools.list_ports.comports() if 'Vodafone' in p.description or 'USB' in p.description]; [print(f'{p.device} - {p.description}') for p in ports]"

# Backend starten
python server_real_rf_system.py --port COM5 --baud 115200
```

### SDR-Geräte
```bash
# RTL-SDR, HackRF, etc.
python server_real_rf_system.py --port /dev/ttyUSB0 --baud 115200
```

### Custom RF-Module
```bash
# ESP32, Arduino, etc. mit RF-Modulen
python server_real_rf_system.py --port COM3 --baud 115200
```

## 📊 Live-Monitoring

### Charts
- **Throughput:** Echtzeit-Geschwindigkeitsanzeige
- **Spektrum:** Frequenz-Leistungs-Diagramm
- **CA-Status:** Carrier Aggregation-Übersicht

### Metriken
- Min/Max/Noise-Pegel
- Aktive Bänder
- TX/RX-Status

## 🔧 Troubleshooting

### Backend startet nicht
```bash
# Port prüfen
python -c "import serial.tools.list_ports; [print(p.device) for p in serial.tools.list_ports.comports()]"

# Dependencies prüfen
pip list | grep -E "(pyserial|websockets)"

# Port-Freigabe prüfen
# (Andere Programme könnten Port blockieren)
```

### WebSocket-Verbindung fehlschlägt
```bash
# Backend-Status prüfen
netstat -an | grep 8765

# Firewall-Einstellungen prüfen
# Port 8765 muss für localhost offen sein
```

### Keine Telemetrie-Daten
```bash
# Serielle Verbindung testen
python -c "
import serial
import time
ser = serial.Serial('COM5', 115200, timeout=1)
for i in range(10):
    try:
        line = ser.readline().decode().strip()
        print(f'Line {i}: {line}')
    except:
        print(f'Line {i}: Error')
    time.sleep(0.1)
ser.close()
"
```

## 📋 Test-Checkliste

- [ ] COM-Port identifiziert
- [ ] Dependencies installiert (`pip install pyserial websockets`)
- [ ] Backend startet ohne Fehler
- [ ] WebSocket auf Port 8765 erreichbar
- [ ] Frontend verbindet sich automatisch
- [ ] Telemetrie-Daten erscheinen in Charts
- [ ] AT-Kommandos werden gesendet
- [ ] Gerät antwortet auf Kommandos

## 🔒 Sicherheitshinweise

- **Nur lokale Verbindungen:** Backend läuft standardmäßig nur auf 127.0.0.1
- **Port-Sicherheit:** Keine Authentifizierung implementiert
- **RF-Compliance:** Beachte lokale Regulierungen für RF-Übertragungen
- **TX-Freigabe:** Sende nur auf erlaubten Frequenzen

## 📈 Erweiterte Konfiguration

### Custom Baud-Rate
```bash
python server_real_rf_system.py --port COM5 --baud 9600
```

### Remote-Zugriff
```bash
python server_real_rf_system.py --port COM5 --host 0.0.0.0 --wsport 8765
```

### Logging aktivieren
```bash
python server_real_rf_system.py --port COM5 --verbose
```

## 🎯 Nächste Schritte

1. **Hardware verbinden** und COM-Port identifizieren
2. **Backend starten** mit korrektem Port
3. **Frontend testen** - Connect-Button klicken
4. **Telemetrie validieren** - Daten sollten in Charts erscheinen
5. **AT-Kommandos testen** - Gerät sollte antworten
6. **Production-Deployment** - System ist bereit für echte RF-Arbeit

---

**Status:** ✅ System bereit für echte RF-Transceiver-Integration
**Letztes Update:** $(date)
**Version:** 1.0.0
