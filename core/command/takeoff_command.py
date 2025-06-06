# core/command/commands/takeoff_command.py

from core.command.base_command import IRunnableCommand
from application.services.flight_state_manager import FlightStateManager
from application.services.master_provider import MasterProvider
from pymavlink import mavutil


class TakeoffCommand(IRunnableCommand):
    """
    Drone'u belirtilen yüksekliğe kaldırır.
    Precondition: ARM edilmiş olmalı + GUIDED modda olmalı
    Postcondition: COMMAND_ACK beklenir
    """

    def __init__(self, altitude: float, notify_user):
        super().__init__(notify_user)
        self.altitude = altitude

    def run(self):
        state = FlightStateManager.get_instance()
        master = MasterProvider.get()

        if not state.armed:
            self.notify("[Uyarı] Takeoff için drone'un ARM edilmiş olması gerekir.")
            return

        if state.mode.upper() != "GUIDED":
            self.notify("[Uyarı] Takeoff yalnızca GUIDED modda mümkündür.")
            return

        self.notify(f"[Bilgi] {self.altitude:.1f} m yüksekliğe kalkış komutu gönderiliyor...")

        try:
            master.mav.command_long_send(
                master.target_system,
                master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                0,
                0, 0, 0, 0, 0, 0, self.altitude
            )
        except Exception as e:
            self.notify(f"[Hata] Takeoff komutu gönderilemedi: {e}")
