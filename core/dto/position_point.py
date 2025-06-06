# core/dto/position_point.py
from dataclasses import asdict, dataclass, field
import json, time

@dataclass(frozen=True)                # ⬅︎ slots çıkarıldı
class PositionPoint:
    yaw: float
    latitude: float
    longitude: float
    t: float = field(default_factory=time.time)   # dinamik zaman damgası

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))
