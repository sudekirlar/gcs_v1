# core/command/land_command.py

from core.command.base_command import IRunnableCommand
from application.services.flight_state_manager import FlightStateManager
from application.services.master_provider import MasterProvider
from pymavlink import mavutil
import time


class LandCommand(IRunnableCommand):
    """
    Drone'u güvenli şekilde inişe geçirir.
    Precondition: ARM edilmiş olmalı
    Postcondition: İrtifa düşüşü gözlemlenmiş olmalı
    """

    def run(self):
        state = FlightStateManager.get_instance()
        master = MasterProvider.get()

        if not state.armed:
            self.notify("[Uyarı] LAND için drone ARM edilmiş olmalı.")
            return

        self.notify("[Bilgi] LAND komutu gönderiliyor...")

        try:
            master.mav.command_long_send(
                master.target_system,
                master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_LAND,
                0,
                0, 0, 0, 0, 0, 0, 0
            )
        except Exception as e:
            self.notify(f"[Hata] LAND komutu gönderilemedi: {e}")
            return

        # Yükseklik takibi (yaklaşık 3 saniye boyunca gözlemle)
        initial_alt = state.altitude
        for _ in range(30):  # 3 saniye boyunca 0.1s aralıkla
            time.sleep(0.1)
            if state.altitude < initial_alt - 1.0:
                self.notify(f"[Başarılı] İniş başladı: {state.altitude:.1f} m")
                return

        # Hâlâ iniş olmamışsa yine de bildir ama temkinli
        self.notify("[Uyarı] LAND komutu gönderildi ancak iniş tespit edilemedi (gecikmiş olabilir).")
