#!/usr/bin/env python3
"""
Vollständiges Hardware-Registry-System für alle RF-Kommunikationsgeräte
Auditierbar, modular, echt - keine Mocks, keine Ausreden
"""

import json
import sqlite3
import hashlib
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

class HardwareType(Enum):
    SDR = "sdr"
    LTE_MODEM = "lte_modem"
    NEURO_DEVICE = "neuro_device"
    CAN_ADAPTER = "can_adapter"
    NFC_READER = "nfc_reader"
    OPTICAL_MODEM = "optical_modem"
    AUDIO_MODEM = "audio_modem"
    BLUETOOTH = "bluetooth"
    WIFI_MODULE = "wifi_module"
    ZIGBEE = "zigbee"

class CommunicationProtocol(Enum):
    ZIGBEE = "zigbee"
    LORA = "lora"
    LORAWAN = "lorawan"
    LTE = "lte"
    NR5G = "nr5g"
    NEURO = "neuro"
    CAN = "can"
    NFC = "nfc"
    OPTICAL = "optical"
    AUDIO = "audio"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"

@dataclass
class HardwareDevice:
    """Vollständige Hardware-Gerätedefinition"""
    id: str
    name: str
    manufacturer: str
    model: str
    hardware_type: HardwareType
    protocols: List[CommunicationProtocol]
    frequency_range: Dict[str, float]  # {"min_hz": 433e6, "max_hz": 915e6}
    power_range: Dict[str, float]      # {"min_dbm": -10, "max_dbm": 20}
    interfaces: List[str]              # ["usb", "i2c", "spi", "uart"]
    driver_info: Dict[str, str]
    compliance_certs: List[str]
    audit_enabled: bool
    created_at: datetime.datetime
    last_seen: Optional[datetime.datetime]
    status: str

@dataclass
class SignalPath:
    """Kompletter Signalpfad-Definition"""
    id: str
    name: str
    tx_device: str
    rx_device: str
    frequency_hz: float
    protocol: CommunicationProtocol
    modulation: str
    bandwidth_hz: float
    power_dbm: float
    created_at: datetime.datetime
    active: bool

@dataclass
class AuditEntry:
    """Vollständige Audit-Trail-Einträge"""
    id: str
    timestamp: datetime.datetime
    device_id: str
    action: str
    frequency_hz: Optional[float]
    protocol: Optional[CommunicationProtocol]
    payload_size: Optional[int]
    payload_hash: Optional[str]
    status: str
    error_message: Optional[str]
    user_id: Optional[str]

class HardwareRegistry:
    """Vollständiges Hardware-Registry-System"""
    
    def __init__(self, db_path: str = "hardware_registry.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialisiere SQLite-Datenbank für Hardware-Registry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hardware-Geräte-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hardware_devices (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                model TEXT NOT NULL,
                hardware_type TEXT NOT NULL,
                protocols TEXT NOT NULL,  -- JSON array
                frequency_range TEXT NOT NULL,  -- JSON object
                power_range TEXT NOT NULL,  -- JSON object
                interfaces TEXT NOT NULL,  -- JSON array
                driver_info TEXT NOT NULL,  -- JSON object
                compliance_certs TEXT NOT NULL,  -- JSON array
                audit_enabled BOOLEAN NOT NULL,
                created_at TEXT NOT NULL,
                last_seen TEXT,
                status TEXT NOT NULL
            )
        """)
        
        # Signalpfade-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_paths (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                tx_device TEXT NOT NULL,
                rx_device TEXT NOT NULL,
                frequency_hz REAL NOT NULL,
                protocol TEXT NOT NULL,
                modulation TEXT NOT NULL,
                bandwidth_hz REAL NOT NULL,
                power_dbm REAL NOT NULL,
                created_at TEXT NOT NULL,
                active BOOLEAN NOT NULL
            )
        """)
        
        # Audit-Trail-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                device_id TEXT NOT NULL,
                action TEXT NOT NULL,
                frequency_hz REAL,
                protocol TEXT,
                payload_size INTEGER,
                payload_hash TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                user_id TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        self.logger.info("Hardware-Registry-Datenbank initialisiert")
    
    def register_device(self, device: HardwareDevice) -> bool:
        """Registriere neues Hardware-Gerät"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO hardware_devices 
                (id, name, manufacturer, model, hardware_type, protocols, 
                 frequency_range, power_range, interfaces, driver_info, 
                 compliance_certs, audit_enabled, created_at, last_seen, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                device.id,
                device.name,
                device.manufacturer,
                device.model,
                device.hardware_type.value,
                json.dumps([p.value for p in device.protocols]),
                json.dumps(device.frequency_range),
                json.dumps(device.power_range),
                json.dumps(device.interfaces),
                json.dumps(device.driver_info),
                json.dumps(device.compliance_certs),
                device.audit_enabled,
                device.created_at.isoformat(),
                device.last_seen.isoformat() if device.last_seen else None,
                device.status
            ))
            
            conn.commit()
            conn.close()
            
            # Audit-Eintrag erstellen
            self._log_audit_entry(
                device_id=device.id,
                action="device_registered",
                status="success"
            )
            
            self.logger.info(f"Gerät registriert: {device.name} ({device.id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler bei Geräteregistrierung: {e}")
            return False
    
    def create_signal_path(self, signal_path: SignalPath) -> bool:
        """Erstelle neuen Signalpfad"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO signal_paths 
                (id, name, tx_device, rx_device, frequency_hz, protocol, 
                 modulation, bandwidth_hz, power_dbm, created_at, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal_path.id,
                signal_path.name,
                signal_path.tx_device,
                signal_path.rx_device,
                signal_path.frequency_hz,
                signal_path.protocol.value,
                signal_path.modulation,
                signal_path.bandwidth_hz,
                signal_path.power_dbm,
                signal_path.created_at.isoformat(),
                signal_path.active
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Signalpfad erstellt: {signal_path.name} ({signal_path.id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler bei Signalpfad-Erstellung: {e}")
            return False
    
    def _log_audit_entry(self, device_id: str, action: str, 
                        frequency_hz: Optional[float] = None,
                        protocol: Optional[CommunicationProtocol] = None,
                        payload_size: Optional[int] = None,
                        payload_data: Optional[bytes] = None,
                        status: str = "success",
                        error_message: Optional[str] = None,
                        user_id: Optional[str] = None):
        """Logge Audit-Eintrag"""
        try:
            audit_id = hashlib.sha256(
                f"{device_id}{action}{datetime.datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]
            
            payload_hash = None
            if payload_data:
                payload_hash = hashlib.sha256(payload_data).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_trail 
                (id, timestamp, device_id, action, frequency_hz, protocol,
                 payload_size, payload_hash, status, error_message, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_id,
                datetime.datetime.now().isoformat(),
                device_id,
                action,
                frequency_hz,
                protocol.value if protocol else None,
                payload_size,
                payload_hash,
                status,
                error_message,
                user_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Fehler beim Audit-Log: {e}")
    
    def get_all_devices(self) -> List[HardwareDevice]:
        """Hole alle registrierten Geräte"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM hardware_devices")
        rows = cursor.fetchall()
        conn.close()
        
        devices = []
        for row in rows:
            device = HardwareDevice(
                id=row[0],
                name=row[1],
                manufacturer=row[2],
                model=row[3],
                hardware_type=HardwareType(row[4]),
                protocols=[CommunicationProtocol(p) for p in json.loads(row[5])],
                frequency_range=json.loads(row[6]),
                power_range=json.loads(row[7]),
                interfaces=json.loads(row[8]),
                driver_info=json.loads(row[9]),
                compliance_certs=json.loads(row[10]),
                audit_enabled=bool(row[11]),
                created_at=datetime.datetime.fromisoformat(row[12]),
                last_seen=datetime.datetime.fromisoformat(row[13]) if row[13] else None,
                status=row[14]
            )
            devices.append(device)
        
        return devices
    
    def get_audit_trail(self, device_id: Optional[str] = None, 
                       limit: int = 100) -> List[AuditEntry]:
        """Hole Audit-Trail"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if device_id:
            cursor.execute("""
                SELECT * FROM audit_trail 
                WHERE device_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (device_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM audit_trail 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        entries = []
        for row in rows:
            entry = AuditEntry(
                id=row[0],
                timestamp=datetime.datetime.fromisoformat(row[1]),
                device_id=row[2],
                action=row[3],
                frequency_hz=row[4],
                protocol=CommunicationProtocol(row[5]) if row[5] else None,
                payload_size=row[6],
                payload_hash=row[7],
                status=row[8],
                error_message=row[9],
                user_id=row[10]
            )
            entries.append(entry)
        
        return entries
    
    def export_audit_report(self, format: str = "json") -> str:
        """Exportiere vollständigen Audit-Report"""
        devices = self.get_all_devices()
        audit_trail = self.get_audit_trail(limit=10000)
        
        report = {
            "export_timestamp": datetime.datetime.now().isoformat(),
            "total_devices": len(devices),
            "total_audit_entries": len(audit_trail),
            "devices": [asdict(device) for device in devices],
            "audit_trail": [asdict(entry) for entry in audit_trail]
        }
        
        if format == "json":
            return json.dumps(report, indent=2, default=str)
        else:
            # CSV oder andere Formate können hier implementiert werden
            return json.dumps(report, indent=2, default=str)

# Vordefinierte Hardware-Geräte für sofortige Nutzung
PREDEFINED_DEVICES = [
    HardwareDevice(
        id="rtl2832u_001",
        name="RTL2832U SDR Stick",
        manufacturer="Realtek",
        model="RTL2832U",
        hardware_type=HardwareType.SDR,
        protocols=[CommunicationProtocol.ZIGBEE, CommunicationProtocol.LORA],
        frequency_range={"min_hz": 24e6, "max_hz": 1.8e9},
        power_range={"min_dbm": -30, "max_dbm": 0},
        interfaces=["usb"],
        driver_info={"driver": "rtl-sdr", "version": "0.6.0"},
        compliance_certs=["CE", "FCC"],
        audit_enabled=True,
        created_at=datetime.datetime.now(),
        last_seen=None,
        status="available"
    ),
    HardwareDevice(
        id="sx1276_001",
        name="SX1276 LoRa Module",
        manufacturer="Semtech",
        model="SX1276",
        hardware_type=HardwareType.SDR,
        protocols=[CommunicationProtocol.LORA, CommunicationProtocol.LORAWAN],
        frequency_range={"min_hz": 137e6, "max_hz": 1020e6},
        power_range={"min_dbm": -20, "max_dbm": 14},
        interfaces=["spi", "uart"],
        driver_info={"driver": "semtech_sx1276", "version": "1.0.0"},
        compliance_certs=["CE", "FCC", "IC"],
        audit_enabled=True,
        created_at=datetime.datetime.now(),
        last_seen=None,
        status="available"
    ),
    HardwareDevice(
        id="openbci_001",
        name="OpenBCI Cyton",
        manufacturer="OpenBCI",
        model="Cyton",
        hardware_type=HardwareType.NEURO_DEVICE,
        protocols=[CommunicationProtocol.NEURO],
        frequency_range={"min_hz": 0.5, "max_hz": 125},  # EEG Frequenzen
        power_range={"min_dbm": -100, "max_dbm": -50},
        interfaces=["usb", "bluetooth"],
        driver_info={"driver": "openbci_python", "version": "4.0.0"},
        compliance_certs=["FDA", "CE_Medical"],
        audit_enabled=True,
        created_at=datetime.datetime.now(),
        last_seen=None,
        status="available"
    )
]

def initialize_registry_with_predefined_devices():
    """Initialisiere Registry mit vordefinierten Geräten"""
    registry = HardwareRegistry()
    
    for device in PREDEFINED_DEVICES:
        registry.register_device(device)
    
    print(f"✅ Registry initialisiert mit {len(PREDEFINED_DEVICES)} vordefinierten Geräten")
    return registry

if __name__ == "__main__":
    # Beispiel-Nutzung
    registry = initialize_registry_with_predefined_devices()
    
    # Audit-Report exportieren
    report = registry.export_audit_report()
    print("📊 Audit-Report:")
    print(report[:500] + "..." if len(report) > 500 else report)
