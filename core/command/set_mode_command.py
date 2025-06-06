# core/command/commands/set_mode_command.py

from core.command.base_command import IRunnableCommand
from application.services.flight_state_manager import FlightStateManager
from application.services.master_provider import MasterProvider
from pymavlink import mavutil


class SetModeCommand(IRunnableCommand):
    """
    Drone modunu değiştiren komut.
    Komut gönderilir, sonucunu GUI CommandAckReceivedEvent üzerinden dinler.
    """

    def __init__(self, target_mode: str, notify_user):
        super().__init__(notify_user)
        self.target_mode = target_mode.upper()

    def run(self):
        state = FlightStateManager.get_instance()
        master = MasterProvider.get()

        if not master:
            self.notify("[Hata] MAVLink bağlantısı yok.")
            return

        try:
            mode_map = master.mode_mapping()
            mode_id = mode_map.get(self.target_mode)
        except Exception as e:
            self.notify(f"[Hata] Mod haritası okunamadı: {e}")
            return

        if mode_id is None:
            self.notify(f"[Uyarı] '{self.target_mode}' geçersiz bir uçuş modu.")
            return

        self.notify(f"[Bilgi] {self.target_mode} moduna geçiş komutu gönderiliyor...")

        try:
            master.mav.set_mode_send(
                master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                mode_id
            )
            # ✅ Komut gönderildi, cevap EventBus ile gelecek.
        except Exception as e:
            self.notify(f"[Hata] Mod komutu gönderilemedi: {e}")


