# core/command/commands/arm_command.py

from core.command.base_command import IRunnableCommand
from application.services.flight_state_manager import FlightStateManager
from application.services.master_provider import MasterProvider
from pymavlink import mavutil


class ArmCommand(IRunnableCommand):
    """
    Drone'u arm eden komut.
    Precondition: GUIDED modda olmalı
    Postcondition: COMMAND_ACK beklenir (GUI tarafında)
    """
    def run(self):
        state = FlightStateManager.get_instance()
        master = MasterProvider.get()

        if state.mode.upper() != "GUIDED":
            self.notify("[Uyarı] ARM için mod GUIDED olmalı.")
            return

        self.notify("[Bilgi] ARM komutu gönderiliyor...")

        try:
            master.mav.command_long_send(
                master.target_system,
                master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0,  # confirmation
                1, 0, 0, 0, 0, 0, 0
            )
        except Exception as e:
            self.notify(f"[Hata] ARM komutu gönderilemedi: {e}")
