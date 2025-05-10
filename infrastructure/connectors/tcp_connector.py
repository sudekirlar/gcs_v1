# gcs/infrastructure/connectors/tcp_connector.py

from core.interfaces.connector_interface import IConnector

class TcpConnector(IConnector):
    """
    TCP bağlantı için sadece IP ve port bilgisi tutar.
    Bağlantıyı artık pymavlink kurar.
    """

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def open(self):
        pass  # Artık gereksiz

    def close(self):
        # Aynı şekilde burada da pymavlink tarafından kapatılıyor.
        pass

    def is_connected(self) -> bool:
        return True  # Ya da False dönebilir. Kullanılmıyorsa kaldırılabilir.

    def get_identifier(self) -> str:
        return f"{self.ip}:{self.port}"
