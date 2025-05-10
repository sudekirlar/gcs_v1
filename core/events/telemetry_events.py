# core/events/telemetry_events.py

class TelemetryDataEvent:
    """
    (Legacy) Tüm telemetri verilerini birlikte taşıyan event.
    Eski sistem için korunur.
    """
    def __init__(self, yaw, pitch, roll, latitude, longitude, altitude, speed, mode, hdop):
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.speed = speed
        self.mode = mode
        self.hdop = hdop


# ✅ Yeni modüler event sınıfları:
class YawPitchRollUpdatedEvent:
    def __init__(self, yaw, pitch, roll):
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll


class GPSUpdatedEvent:
    def __init__(self, latitude, longitude, altitude):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude


class SpeedUpdatedEvent:
    def __init__(self, speed):
        self.speed = speed


class HDOPUpdatedEvent:
    def __init__(self, hdop):
        self.hdop = hdop


class ModeUpdatedEvent:
    def __init__(self, mode):
        self.mode = mode
