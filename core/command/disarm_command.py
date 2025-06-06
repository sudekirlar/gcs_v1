# core/command/commands/disarm_command.py

from core.command.base_command import IRunnableCommand
from application.services.flight_state_manager import FlightStateManager
from application.services.master_provider import MasterProvider
from pymavlink import mavutil


class DisarmCommand(IRunnableCommand):
    """
    Drone'u disarm eden komut.
    Precondition: Zaten disarm durumda değilse çalıştırılır.
    Postcondition: COMMAND_ACK beklenir
    """

    def run(self):
        state = FlightStateManager.get_instance()
        master = MasterProvider.get()

        if not state.armed:
            self.notify("[Uyarı] Drone zaten disarm durumda.")
            return

        self.notify("[Bilgi] DISARM komutu gönderiliyor...")

        try:
            master.mav.command_long_send(
                master.target_system,
                master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0,  # confirmation
                0, 0, 0, 0, 0, 0, 0  # param1 = 0 → disarm
            )
        except Exception as e:
            self.notify(f"[Hata] DISARM komutu gönderilemedi: {e}")
