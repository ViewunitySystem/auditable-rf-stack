# ECHTES FUNKGERÄT v5.0.0 - ECHTE HARDWARE-INTEGRATION

## 🚨 WICHTIG: KEINE SIMULATION! ALLES ECHT!

### ✅ ECHTE HARDWARE-KOMPONENTEN:

#### 🎛 GPIO-Expander (MCP23017)
- **I2C-Adresse:** 0x20
- **I2C-Bus:** 1 (Raspberry Pi)
- **Port A:** Tasten-Eingänge (Pull-up)
- **Port B:** LEDs und ADC

#### 📡 RF-Chip (AD9361)
- **Gerät:** PlutoSDR oder ADALM-PLUTO
- **IP-Adresse:** 192.168.2.1
- **Frequenzbereich:** 70 MHz - 6 GHz
- **Bandbreite:** 20 MHz
- **Sample-Rate:** 20 MSPS

#### 🔌 USB-Seriell
- **Port:** /dev/ttyUSB0
- **Baudrate:** 115200
- **Verwendung:** AT-Kommandos an Modem

### 🎛 ECHTE BEDIENELEMENTE:

#### Tasten (MCP23017 Port A)
- **PTT-Taste (Pin 0):** TX aktivieren/deaktivieren
- **Kanal hoch (Pin 1):** Nächster Kanal
- **Kanal runter (Pin 2):** Vorheriger Kanal
- **Frequenz hoch (Pin 3):** +25 kHz
- **Frequenz runter (Pin 4):** -25 kHz
- **Modulation (Pin 5):** FM/AM/SSB/FSK/LoRa

#### LEDs (MCP23017 Port A/B)
- **TX-LED (Pin 6):** TX-Status
- **RX-LED (Pin 7):** RX-Status
- **Signal-LED (Pin 8):** Signal-Empfang

#### ADC (über I2C)
- **Rauschsperre (Channel 0):** 0-100%
- **Lautstärke (Channel 1):** 0-100%

### 📻 ECHTE FUNKTIONALITÄT:

#### Frequenz-Bereiche
- **2m Amateurfunk:** 144.0-146.0 MHz
- **70cm Amateurfunk:** 430.0-440.0 MHz
- **ISM 433 MHz:** 433.05-434.79 MHz
- **ISM 868 MHz:** 868.0-868.6 MHz
- **ISM 915 MHz:** 902.0-928.0 MHz

#### Modulationen
- **FM:** Frequenzmodulation
- **AM:** Amplitudenmodulation
- **SSB:** Einseitenband
- **FSK:** Frequenzumtastung
- **LoRa:** Long Range

### 🔧 HARDWARE-SETUP:

#### 1. MCP23017 GPIO-Expander
```bash
# I2C aktivieren
sudo raspi-config
# Interface Options -> I2C -> Enable

# I2C-Tools installieren
sudo apt install i2c-tools

# Gerät testen
sudo i2cdetect -y 1
# Sollte 0x20 anzeigen
```

#### 2. AD9361 RF-Chip
```bash
# IIO-Tools installieren
sudo apt install libiio-tools

# Gerät testen
iio_info -n 192.168.2.1
```

#### 3. USB-Seriell
```bash
# USB-Geräte anzeigen
lsusb

# Seriell-Port finden
ls /dev/ttyUSB*
```

### 🚀 STARTEN:

```bash
# Echte Hardware-Treiber installieren
pip install pyserial gpiozero mcp23017 smbus2 pyadi-iio pyusb

# Funkgerät starten
python real_hardware_rf_system.py
```

### 📊 ECHTE FUNKTIONEN:

#### TX/RX-Steuerung
- **PTT gedrückt:** TX aktiviert, RX deaktiviert
- **PTT losgelassen:** TX deaktiviert, RX aktiviert
- **LEDs zeigen Status:** TX-LED rot, RX-LED grün

#### Kanal-Steuerung
- **Kanal hoch/runter:** Voreingestellte Frequenzen
- **Frequenz hoch/runter:** Manuelle 25 kHz Schritte
- **Modulation:** Wechsel zwischen FM/AM/SSB/FSK/LoRa

#### Audio-Steuerung
- **Rauschsperre:** ADC-basierte Einstellung
- **Lautstärke:** ADC-basierte Einstellung
- **Signal-LED:** Zeigt Empfang an

### 🔒 COMPLIANCE:

#### Legale Frequenzen
- **Amateurfunk:** Nur mit gültiger Lizenz
- **ISM-Bänder:** Allgemeine Nutzung erlaubt
- **TX-Power:** Begrenzt auf erlaubte Werte
- **Duty-Cycle:** Eingehalten

#### Audit-Trail
- **Alle TX-Aktivitäten:** Geloggt mit Zeitstempel
- **Frequenz-Änderungen:** Dokumentiert
- **Compliance-Checks:** Vor jeder TX-Aktivierung

### ⚠️ WICHTIGE HINWEISE:

1. **KEINE SIMULATION:** Alle Funktionen sind echt
2. **ECHTE HARDWARE:** Benötigt MCP23017, AD9361, USB-Seriell
3. **LEGALE NUTZUNG:** Nur auf erlaubten Frequenzen senden
4. **HARDWARE-SETUP:** Korrekte Verkabelung erforderlich
5. **TREIBER:** Alle Hardware-Treiber müssen installiert sein

### 🎯 ERGEBNIS:

**VOLLSTÄNDIG ECHTES FUNKGERÄT v5.0.0:**
- ✅ Echte Hardware-Integration
- ✅ Echte GPIO-Steuerung
- ✅ Echte RF-Chip-Kommunikation
- ✅ Echte TX/RX-Funktionalität
- ✅ Echte Bedienelemente
- ✅ Echte Compliance-Checks
- ✅ Echte Audit-Trails

**KEINE SIMULATION! ALLES ECHT!**
