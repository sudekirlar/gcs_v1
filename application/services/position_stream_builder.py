# application/services/position_stream_builder.py

from utils.event_bus import EventBus
from core.events.telemetry_events import (
    YawPitchRollUpdatedEvent, GPSUpdatedEvent, PositionPointReadyEvent
)
from core.dto.position_point import PositionPoint

class PositionStreamBuilder:
    """YPR + GPS → PositionPoint JSON akışını üretir (stateless outside GUI)."""

    def __init__(self):
        self._yaw = None     # son bilinenler
        self._lat = None
        self._lon = None

        # EventBus aboneliklerini kendi içinde yapıyoruz
        EventBus.subscribe(YawPitchRollUpdatedEvent, self._on_ypr)
        EventBus.subscribe(GPSUpdatedEvent,            self._on_gps)

    # ---------- internal subscribers ----------
    def _on_ypr(self, evt: YawPitchRollUpdatedEvent):
        self._yaw = evt.yaw
        self._try_emit()

    def _on_gps(self, evt: GPSUpdatedEvent):
        self._lat, self._lon = evt.latitude, evt.longitude
        self._try_emit()

    def _try_emit(self):
        if None not in (self._yaw, self._lat, self._lon):
            point = PositionPoint(self._yaw, self._lat, self._lon)
            print("[JSON]", point.to_json())
            EventBus.publish(PositionPointReadyEvent(point))
