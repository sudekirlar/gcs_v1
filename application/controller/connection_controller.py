# application/controller/connection_controller.py

from core.interfaces.connector_interface import IConnector
from utils.event_bus import EventBus
from core.events.connection_events import ConnectionClosedEvent
from application.services.master_provider import MasterProvider
from pymavlink import mavutil
from PyQt5.QtCore import QThreadPool
from application.workers.open_mavlink_connection_worker import OpenPymavlinkConnectionWorker
from serial.tools import list_ports
from infrastructure.connectors.serial_connector import SerialConnector
from infrastructure.connectors.tcp_connector import TcpConnector


class ConnectionController:
    """
    Arayüzden gelen bağlantı açma/kapama isteklerini yöneten sınıf.
    """

    def __init__(self):
        self.active_connector: IConnector = None
        self.master = None

    def connect_serial(self, port: str, baudrate: int = 57600):
        """
        pymavlink ile seri bağlantı başlatır (thread içinde).
        """
        self.active_connector = SerialConnector(port, baudrate)

        worker = OpenPymavlinkConnectionWorker("serial", port, baudrate)
        QThreadPool.globalInstance().start(worker)

    def connect_tcp(self, ip: str, port: int):
        """
        pymavlink ile TCP bağlantı başlatır (thread içinde).
        """
        self.active_connector = TcpConnector(ip, port)

        worker = OpenPymavlinkConnectionWorker("tcp", ip, port)
        QThreadPool.globalInstance().start(worker)

    def disconnect(self):
        """
        Tüm bağlantı nesnelerini kapatır ve EventBus ile yayar.
        """
        if self.active_connector and self.active_connector.is_connected():
            self.active_connector.close()
            EventBus.publish(ConnectionClosedEvent(self.active_connector.get_identifier()))
            self.active_connector = None

        try:
            master = MasterProvider.get()
            master.close()
            print("[INFO] pymavlink bağlantısı kapatıldı.")
        except Exception as e:
            print(f"[WARN] pymavlink bağlantısı kapanırken hata: {e}")
        finally:
            MasterProvider.clear()

    def get_current_connection_id(self) -> str:
        if self.active_connector:
            return self.active_connector.get_identifier()
        return "Bağlantı Yok"

    def get_available_ports(self) -> list[str]:
        """
        TCP seçeneği dahil, sistemdeki kullanılabilir bağlantıları listeler.
        """
        ports = list_ports.comports()
        port_names = [port.device for port in ports]
        return ["TCP (127.0.0.1:5760)"] + port_names