# utils/event_dispatcher.py

from PyQt5.QtCore import QObject, pyqtSignal
from core.events.connection_events import (
    ConnectionOpenedEvent,
    ConnectionClosedEvent,
    ConnectionFailedEvent,
)
from core.events.telemetry_events import (
    TelemetryDataEvent,
    YawPitchRollUpdatedEvent,
    GPSUpdatedEvent,
    SpeedUpdatedEvent,
    HDOPUpdatedEvent,
    ModeUpdatedEvent,
)


class EventDispatcher(QObject):
    """
    EventBus'tan gelen olayları Qt sinyallerine dönüştürerek
    GUI thread'ine güvenli şekilde ileten dispatcher sınıfı.
    """

    # Bağlantı sinyalleri
    connectionOpened = pyqtSignal(ConnectionOpenedEvent)
    connectionClosed = pyqtSignal(ConnectionClosedEvent)
    connectionFailed = pyqtSignal(ConnectionFailedEvent)

    # (Legacy) Tüm veriyi birlikte yayan event
    telemetryReceived = pyqtSignal(TelemetryDataEvent)

    # ✅ Yeni modüler telemetry sinyalleri
    yawPitchRollUpdated = pyqtSignal(YawPitchRollUpdatedEvent)
    gpsUpdated = pyqtSignal(GPSUpdatedEvent)
    speedUpdated = pyqtSignal(SpeedUpdatedEvent)
    hdopUpdated = pyqtSignal(HDOPUpdatedEvent)
    modeUpdated = pyqtSignal(ModeUpdatedEvent)

    def __init__(self):
        super().__init__()

    def dispatch(self, event):
        """
        EventBus üzerinden gelen event'leri ilgili Qt sinyallerine yönlendirir.
        Böylece slotlar GUI thread'inde güvenli şekilde çalışır.
        """
        if isinstance(event, ConnectionOpenedEvent):
            self.connectionOpened.emit(event)
        elif isinstance(event, ConnectionClosedEvent):
            self.connectionClosed.emit(event)
        elif isinstance(event, ConnectionFailedEvent):
            self.connectionFailed.emit(event)
        elif isinstance(event, TelemetryDataEvent):
            self.telemetryReceived.emit(event)
        elif isinstance(event, YawPitchRollUpdatedEvent):
            self.yawPitchRollUpdated.emit(event)
        elif isinstance(event, GPSUpdatedEvent):
            self.gpsUpdated.emit(event)
        elif isinstance(event, SpeedUpdatedEvent):
            self.speedUpdated.emit(event)
        elif isinstance(event, HDOPUpdatedEvent):
            self.hdopUpdated.emit(event)
        elif isinstance(event, ModeUpdatedEvent):
            self.modeUpdated.emit(event)
        else:
            print(f"[WARN] EventDispatcher: Bilinmeyen event tipi {type(event)}")
