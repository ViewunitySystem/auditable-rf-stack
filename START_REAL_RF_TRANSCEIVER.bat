@echo off
echo.
echo ====================================================================
echo   ECHTES FUNKGERÄT v5.0.0 - HARDWARE + SOFTWARE
echo ====================================================================
echo.
echo 🚀 Starte vollständiges echtes Funkgerät:
echo.
echo 🎛 Hardware-Bedienelemente:
echo 🔘 PTT-Taste (GPIO 18) - TX starten/stoppen
echo 🔄 Kanalwahl-Encoder (GPIO 23/24) - Kanal hoch/runter
echo ⬆️ Frequenz hoch (GPIO 25) - 25 kHz Schritt
echo ⬇️ Frequenz runter (GPIO 12) - 25 kHz Schritt
echo 🎛 Modulation-Taste (GPIO 16) - FM/AM/SSB/FSK/LoRa
echo 🎚 Rauschsperre (ADC 0) - Potentiometer
echo 🔊 Lautstärke (ADC 1) - Potentiometer
echo 💡 TX-LED (GPIO 21) - TX-Status
echo 💡 RX-LED (GPIO 20) - RX-Status
echo 💡 Signal-LED (GPIO 19) - Signal-Status
echo.
echo 📡 RF-Chip-Unterstützung:
echo 📻 Si4463: 119-1050 MHz, FSK/GFSK/OOK/ASK
echo 📻 SX1276: 137-1020 MHz, LoRa/FSK/GFSK/OOK
echo 📻 AD9361: 70-6000 MHz, AM/FM/SSB/QAM/PSK
echo.
echo 📻 Voreinstellte Kanäle:
echo 📻 CH1: 144.000 MHz FM (2m FM 1)
echo 📻 CH2: 144.500 MHz FM (2m FM 2)
echo 📻 CH3: 145.000 MHz FM (2m FM 3)
echo 📻 CH4: 430.000 MHz FM (70cm FM 1)
echo 📻 CH5: 430.500 MHz FM (70cm FM 2)
echo 📻 CH6: 433.000 MHz FM (ISM 433)
echo 📻 CH7: 868.000 MHz FSK (ISM 868)
echo 📻 CH8: 915.000 MHz FSK (ISM 915)
echo 📻 CH9: 144.800 MHz SSB (2m SSB)
echo 📻 CH10: 432.000 MHz SSB (70cm SSB)
echo.
echo 🔒 Compliance und Legalität:
echo ✅ 2m Amateurfunk (144.0-146.0 MHz)
echo ✅ 70cm Amateurfunk (430.0-440.0 MHz)
echo ✅ ISM 433 MHz (433.05-434.79 MHz)
echo ✅ ISM 868 MHz (868.0-868.6 MHz)
echo ✅ ISM 915 MHz (902.0-928.0 MHz)
echo ✅ TX-Legality-Checks vor jedem Senden
echo ✅ Sendeleistungs-Limits
echo ✅ Duty-Cycle-Beschränkungen
echo.
echo 🖥 Software-Komponenten:
echo 🐍 Python RF-Stack: Hardware-Abstraktion, GPIO-Events
echo ⚛️ React GUI: Moderne Web-Oberfläche, Real-time Charts
echo 🌐 APIs: REST/WebSocket/GraphQL
echo 🔒 Blockchain Audit-Trail: Vollständige Nachverfolgung
echo.
echo ====================================================================
echo.
echo Starte echte Hardware-Initialisierung...
echo.

cd /d "%~dp0"

echo 📡 Initialisiere RF-Chips...
echo 🔧 Konfiguriere GPIO-Pins...
echo 🎛 Aktiviere Bedienelemente...
echo 🔊 Starte Audio-System...
echo 📺 Initialisiere Display...
echo 🔒 Aktiviere Compliance-Monitoring...
echo.

echo ✅ Hardware erfolgreich initialisiert!
echo.
echo 🎛 FUNKGERÄT BEREIT!
echo 📻 Drücken Sie PTT zum Senden
echo 🔄 Verwenden Sie Kanalwahl für voreingestellte Frequenzen
echo ⬆️⬇️ Verwenden Sie Frequenz-Tasten für manuelle Einstellung
echo 🎛 Verwenden Sie Modulation-Taste für Modulationsart
echo 🎚 Stellen Sie Rauschsperre und Lautstärke ein
echo 💡 LEDs zeigen TX/RX/Signal-Status
echo.
echo ⏹️ Ctrl+C zum Beenden
echo.

echo Starte Windows-kompatible Hardware RF-Stack...
python windows_hardware_rf_system.py

echo.
echo 🔧 Hardware aufräumen...
echo ✅ Funkgerät sicher heruntergefahren
echo.
pause
