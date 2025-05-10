# application/services/flight_state_manager.py

class FlightStateManager:
    """
    Telemetry verilerinin son halini tutan singleton sınıf.
    Komutlar bu sınıfı okuyarak pre/post-condition kontrolü yapar.
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.mode = ""
        self.armed = False
        self.altitude = 0.0

    def update_mode(self, mode: str):
        self.mode = mode

    def update_armed(self, base_mode: int):
        # MAV_MODE_FLAG_SAFETY_ARMED = 0b10000000
        self.armed = (base_mode & 0b10000000) > 0

    def update_altitude(self, altitude: float):
        self.altitude = altitude
