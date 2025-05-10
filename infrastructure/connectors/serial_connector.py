# gcs/infrastructure/connectors/serial_connector.py

from core.interfaces.connector_interface import IConnector

class SerialConnector(IConnector):
    """
    Sadece port bilgisini ve GUI için tanımlayıcıyı tutar.
    Fiziksel bağlantı pymavlink tarafından açılır.
    """

    def __init__(self, port: str, baudrate: int = 57600):
        self.port = port
        self.baudrate = baudrate

    def open(self):
        pass  # Artık kullanılmıyor

    def close(self):
        # Serial bağlantı pymavlink tarafından açıldığı için burada doğrudan bir kapatma yok.
        # Ancak GUI'den gelen bağlantı kapatma isteği ile uyumlu kalmak adına metod korunuyor.
        pass

    def is_connected(self) -> bool:
        # Eğer kullanılmıyorsa bu metod tamamen kaldırılabilir.
        return True

    def get_identifier(self) -> str:
        return self.port
