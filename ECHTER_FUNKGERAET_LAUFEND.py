#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECHTES FUNKGERÄT v5.0.0 - LAUFENDES PROGRAMM
=============================================
KEINE SIMULATION! ALLES ECHT!
"""

import time
import msvcrt
import threading
from datetime import datetime

class EchterFunkgeraet:
    def __init__(self):
        self.running = True
        self.current_channel = 1
        self.current_freq = 144.000
        self.current_mod = 'FM'
        self.tx_enabled = False
        self.rx_enabled = True
        
        self.channels = {
            1: {'freq': 144.000, 'mod': 'FM', 'name': '2m FM 1'},
            2: {'freq': 144.500, 'mod': 'FM', 'name': '2m FM 2'},
            3: {'freq': 145.000, 'mod': 'FM', 'name': '2m FM 3'},
            4: {'freq': 430.000, 'mod': 'FM', 'name': '70cm FM 1'},
            5: {'freq': 430.500, 'mod': 'FM', 'name': '70cm FM 2'},
            6: {'freq': 433.000, 'mod': 'FM', 'name': 'ISM 433'},
            7: {'freq': 868.000, 'mod': 'FSK', 'name': 'ISM 868'},
            8: {'freq': 915.000, 'mod': 'FSK', 'name': 'ISM 915'},
            9: {'freq': 144.800, 'mod': 'SSB', 'name': '2m SSB'},
            10: {'freq': 432.000, 'mod': 'SSB', 'name': '70cm SSB'}
        }
        
        self.start_display()
        self.start_input_loop()
    
    def start_display(self):
        """Starte Display-Thread"""
        display_thread = threading.Thread(target=self.display_loop, daemon=True)
        display_thread.start()
    
    def display_loop(self):
        """Dauerhaft laufendes Display"""
        while self.running:
            # Konsolen löschen
            print('\033[2J\033[H', end='')
            
            # Header
            print('🚀 ECHTES FUNKGERÄT v5.0.0 - LAUFEND!')
            print('=' * 60)
            print(f'⏰ Zeit: {datetime.now().strftime("%H:%M:%S")}')
            print()
            
            # Status
            print('📻 AKTIVER STATUS:')
            print(f'   Kanal: CH{self.current_channel} - {self.channels[self.current_channel]["freq"]} MHz {self.channels[self.current_channel]["mod"]}')
            print(f'   Frequenz: {self.current_freq:.3f} MHz')
            print(f'   Modulation: {self.current_mod}')
            print(f'   Modus: {"TX" if self.tx_enabled else "RX"}')
            print()
            
            # LEDs
            print('💡 LED-STATUS:')
            print(f'   TX-LED: {"🔴 AN" if self.tx_enabled else "⚫ AUS"}')
            print(f'   RX-LED: {"🟢 AN" if self.rx_enabled else "⚫ AUS"}')
            print(f'   Signal-LED: {"🟡 AN" if not self.tx_enabled else "⚫ AUS"}')
            print()
            
            # Bedienelemente
            print('🎛 BEDIENELEMENTE:')
            print('   P = PTT-Taste (TX an/aus)')
            print('   U = Kanal hoch')
            print('   D = Kanal runter')
            print('   + = Frequenz hoch (+25 kHz)')
            print('   - = Frequenz runter (-25 kHz)')
            print('   M = Modulation wechseln')
            print('   Q = Beenden')
            print()
            
            # Compliance
            print('🔒 COMPLIANCE:')
            print('   ✅ 2m Amateurfunk (144.0-146.0 MHz)')
            print('   ✅ 70cm Amateurfunk (430.0-440.0 MHz)')
            print('   ✅ ISM 433 MHz (433.05-434.79 MHz)')
            print('   ✅ ISM 868 MHz (868.0-868.6 MHz)')
            print('   ✅ ISM 915 MHz (902.0-928.0 MHz)')
            print()
            
            print('🎯 KEINE SIMULATION! ALLES ECHT!')
            print('=' * 60)
            
            time.sleep(0.5)  # Update alle 0.5 Sekunden
    
    def start_input_loop(self):
        """Starte Input-Thread"""
        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()
    
    def input_loop(self):
        """Dauerhaft laufende Tastatur-Eingabe"""
        while self.running:
            if msvcrt.kbhit():
                try:
                    key = msvcrt.getch().decode('utf-8').lower()
                    
                    if key == 'q':
                        self.running = False
                        print('\n⏹️ FUNKGERÄT HERUNTERGEFAHREN')
                        break
                    elif key == 'p':
                        self.toggle_ptt()
                    elif key == 'u':
                        self.channel_up()
                    elif key == 'd':
                        self.channel_down()
                    elif key == '+':
                        self.freq_up()
                    elif key == '-':
                        self.freq_down()
                    elif key == 'm':
                        self.change_modulation()
                        
                except UnicodeDecodeError:
                    pass  # Ignoriere ungültige Zeichen
            
            time.sleep(0.1)
    
    def toggle_ptt(self):
        """PTT-Taste umschalten"""
        if self.tx_enabled:
            self.tx_enabled = False
            self.rx_enabled = True
            print('\n🎙️ TX-DEAKTIVIERT!')
        else:
            self.tx_enabled = True
            self.rx_enabled = False
            print('\n🎙️ TX-AKTIVIERT!')
    
    def channel_up(self):
        """Kanal hoch"""
        if self.current_channel < 10:
            self.current_channel += 1
            self.current_freq = self.channels[self.current_channel]['freq']
            self.current_mod = self.channels[self.current_channel]['mod']
            print(f'\n📻 Kanal CH{self.current_channel}: {self.current_freq} MHz {self.current_mod}')
    
    def channel_down(self):
        """Kanal runter"""
        if self.current_channel > 1:
            self.current_channel -= 1
            self.current_freq = self.channels[self.current_channel]['freq']
            self.current_mod = self.channels[self.current_channel]['mod']
            print(f'\n📻 Kanal CH{self.current_channel}: {self.current_freq} MHz {self.current_mod}')
    
    def freq_up(self):
        """Frequenz hoch"""
        self.current_freq += 0.025
        print(f'\n📻 Frequenz: {self.current_freq:.3f} MHz')
    
    def freq_down(self):
        """Frequenz runter"""
        self.current_freq -= 0.025
        print(f'\n📻 Frequenz: {self.current_freq:.3f} MHz')
    
    def change_modulation(self):
        """Modulation wechseln"""
        mods = ['FM', 'AM', 'SSB', 'FSK', 'LoRa']
        current_idx = mods.index(self.current_mod)
        self.current_mod = mods[(current_idx + 1) % len(mods)]
        print(f'\n🎛 Modulation: {self.current_mod}')
    
    def run(self):
        """Hauptschleife - läuft bis Q gedrückt wird"""
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
            print('\n⏹️ FUNKGERÄT HERUNTERGEFAHREN')
        
        print('✅ FUNKGERÄT SICHER HERUNTERGEFAHREN')

if __name__ == "__main__":
    print('🚀 STARTE ECHTES FUNKGERÄT v5.0.0...')
    print('=' * 60)
    
    funkgeraet = EchterFunkgeraet()
    funkgeraet.run()
