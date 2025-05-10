# application/workers/open_mavlink_connection_worker.py

from PyQt5.QtCore import QRunnable
from pymavlink import mavutil
from core.events.connection_events import ConnectionOpenedEvent, ConnectionFailedEvent
from utils.event_bus import EventBus
from application.services.master_provider import MasterProvider

class OpenPymavlinkConnectionWorker(QRunnable):
    """
    pymavlink üzerinden seri veya TCP bağlantı kurar.
    Bu sınıf, bağlantıyı arka planda kurarak GUI donmasını engeller.
    Bağlantı başarılı olursa master nesnesini MasterProvider ile paylaşır.
    """

    def __init__(self, conn_type: str, address: str, port_or_baud: int):
        """
        :param conn_type: "serial" veya "tcp"
        :param address: serial için port adı (örn: "COM7"), TCP için IP adresi (örn: "127.0.0.1")
        :param port_or_baud: serial için baudrate (örn: 57600), TCP için port (örn: 5760)
        """
        super().__init__()
        self.conn_type = conn_type
        self.address = address
        self.port_or_baud = port_or_baud

    def run(self):
        try:
            # MAVLink bağlantısını başlat
            if self.conn_type == "serial":
                print(f"[MAVLINK] SERIAL bağlantısı başlatılıyor: {self.address} @ {self.port_or_baud}")
                master = mavutil.mavlink_connection(
                    device=self.address,
                    baud=self.port_or_baud,
                    autoreconnect=True
                )
            else:
                print(f"[MAVLINK] TCP bağlantısı başlatılıyor: tcp:{self.address}:{self.port_or_baud}")
                master = mavutil.mavlink_connection(
                    f"tcp:{self.address}:{self.port_or_baud}",
                    autoreconnect=True
                )

            # Heartbeat bekleniyor
            print("[MAVLINK] Heartbeat bekleniyor...")
            master.wait_heartbeat(timeout=10)
            print("[MAVLINK] Heartbeat alındı.")

            # Master'ı global yap
            MasterProvider.set(master)

            # EventBus ile bağlantı açıldığını yay
            EventBus.publish(ConnectionOpenedEvent(f"{self.address}:{self.port_or_baud}"))

        except Exception as e:
            print(f"[ERROR] pymavlink bağlantı hatası: {e}")
            EventBus.publish(ConnectionFailedEvent(str(e)))
