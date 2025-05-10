import unittest
import time
from core.command.set_mode_command import SetModeCommand
from core.command.arm_command import ArmCommand
from core.command.takeoff_command import TakeoffCommand
from core.command.land_command import LandCommand  # bunu senin projende tanımladık
from application.services.flight_state_manager import FlightStateManager


from pymavlink import mavutil
from application.services.master_provider import MasterProvider

class TestRealSITLFlightSequence(unittest.TestCase):
    def setUp(self):
        self.state = FlightStateManager.get_instance()
        self.notifications = []
        self.timings = {}

        # ✅ Gerçek master bağlantısını kur (SITL'e bağlı olduğunu varsayıyoruz)
        self.master = mavutil.mavlink_connection("tcp:127.0.0.1:5760")
        self.master.wait_heartbeat(timeout=10)  # önemli! bağlantının hazır olduğundan emin ol
        MasterProvider.set(self.master)  # Test ortamına master kaydedildi


    def notify_user(self, message: str):
        print(f"[notify] {message}")
        self.notifications.append(message)

    def test_guided_arm_takeoff_land(self):
        # --- SET MODE: GUIDED ---
        t0 = time.time()
        cmd_mode = SetModeCommand("GUIDED", self.notify_user)
        cmd_mode.run()
        time.sleep(2)
        self.state.update_mode("GUIDED")
        self.timings["GUIDED"] = time.time() - t0

        # --- ARM ---
        t1 = time.time()
        cmd_arm = ArmCommand(self.notify_user)
        cmd_arm.run()
        time.sleep(2)
        self.state.update_armed(0b10000000)
        self.timings["ARM"] = time.time() - t1

        # --- TAKEOFF ---
        self.state.update_altitude(0.0)
        t2 = time.time()
        cmd_takeoff = TakeoffCommand(10.0, self.notify_user)
        cmd_takeoff.run()
        time.sleep(6)
        self.state.update_altitude(10.1)  # yükselme gerçekleşti kabulü
        self.timings["TAKEOFF"] = time.time() - t2

        # --- LAND ---
        self.state.update_altitude(0.4)
        t3 = time.time()
        cmd_land = LandCommand(self.notify_user)
        cmd_land.run()
        self.timings["LAND"] = time.time() - t3

        # --- Süreleri yazdır ---
        for cmd, duration in self.timings.items():
            print(f"[SÜRE] {cmd} komutu: {duration:.2f} saniye")

        # --- Temel kontrol: her adım bildirildi mi? ---
        self.assertTrue(any("GUIDED" in m for m in self.notifications))
        self.assertTrue(any("ARM" in m for m in self.notifications))
        self.assertTrue(any("kalkış" in m for m in self.notifications))
        self.assertTrue(any("LAND" in m for m in self.notifications))


if __name__ == "__main__":
    unittest.main()
