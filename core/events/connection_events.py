# core/events/connection_events.py

class ConnectionOpenedEvent:
    """
    Bağlantı başarıyla kurulduğunda tetiklenen event.
    """
    def __init__(self, identifier: str):
        self.identifier = identifier  # Örn: 'COM7' veya '127.0.0.1:5760'


class ConnectionFailedEvent:
    """
    Bağlantı kurulamadığında tetiklenen event.
    """
    def __init__(self, error: str):
        self.error = error  # Hata mesajı


class ConnectionClosedEvent:
    """
    Bağlantı kapatıldığında tetiklenen event.
    """
    def __init__(self, identifier: str):
        self.identifier = identifier  # Örn: 'COM7' veya '127.0.0.1:5760'