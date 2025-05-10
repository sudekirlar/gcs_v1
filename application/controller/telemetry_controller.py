# application/controller/telemetry_controller.py

import threading
import math

from pymavlink import mavutil
from application.services.master_provider import MasterProvider
from application.services.flight_state_manager import FlightStateManager

from utils.event_bus import EventBus
from core.events.telemetry_events import (
    YawPitchRollUpdatedEvent,
    GPSUpdatedEvent,
    SpeedUpdatedEvent,
    HDOPUpdatedEvent,
    ModeUpdatedEvent
)
from core.events.command_events import CommandAckReceivedEvent

class TelemetryController:
    """
    Telemetri verilerini pymavlink üzerinden okuyup EventBus ile yayınlar.
    Aynı zamanda FlightStateManager ile son durumu günceller.
    """

    def __init__(self):
        self._running = False
        self._thread = None
        self.master = None

        self._yaw = 0.0
        self._pitch = 0.0
        self._roll = 0.0
        self._lat = 0.0
        self._lon = 0.0
        self._alt = 0.0
        self._mode = ""
        self._speed = 0.0
        self._hdop = 0.0

        self._state = FlightStateManager.get_instance()

    def start(self):
        self.stop()

        try:
            self.master = MasterProvider.get()
        except Exception as e:
            print(f"[ERROR] TelemetryController başlatılamadı (master alınamadı): {e}")
            return

        try:
            stream_requests = [
                ("MAV_DATA_STREAM_RAW_SENSORS", 10),
                ("MAV_DATA_STREAM_EXTENDED_STATUS", 5),
                ("MAV_DATA_STREAM_POSITION", 10),
                ("MAV_DATA_STREAM_EXTRA1", 10),
                ("MAV_DATA_STREAM_EXTRA2", 5),
            ]
            for stream_name, rate in stream_requests:
                stream_id = getattr(mavutil.mavlink, stream_name, None)
                if stream_id is not None:
                    self.master.mav.request_data_stream_send(
                        self.master.target_system,
                        self.master.target_component,
                        stream_id,
                        rate,
                        start_stop=1
                    )
            print("[INFO] MAVLink stream istekleri gönderildi.")
        except Exception as e:
            print(f"[WARN] Stream başlatma hatası: {e}")

        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        print("[INFO] TelemetryController başlatıldı.")

    def stop(self):
        if self._running:
            self._running = False
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=1)
                print("[INFO] Telemetri thread durduruldu.")
            self._thread = None
        else:
            print("[INFO] Telemetri zaten durmuş durumda.")

    def _read_loop(self):
        print("[TELEMETRY] Telemetri okuma başlatıldı.")
        while self._running:
            try:
                msg = self.master.recv_match(blocking=True, timeout=1)
                if msg:
                    self._handle_message(msg)
            except Exception as e:
                print(f"[ERROR] Telemetri okuma hatası: {e}")

    def _handle_message(self, msg):
        t = msg.get_type()

        if t == "ATTITUDE":
            self._yaw = (math.degrees(msg.yaw) + 360) % 360
            self._pitch = math.degrees(msg.pitch)
            self._roll = math.degrees(msg.roll)
            EventBus.publish(YawPitchRollUpdatedEvent(self._yaw, self._pitch, self._roll))

        elif t == "GLOBAL_POSITION_INT":
            self._lat = msg.lat / 1e7
            self._lon = msg.lon / 1e7
            self._alt = msg.alt / 1000.0
            EventBus.publish(GPSUpdatedEvent(self._lat, self._lon, self._alt))

            self._state.update_altitude(self._alt)

        elif t == "GPS_RAW_INT":
            self._hdop = msg.eph / 100.0
            EventBus.publish(HDOPUpdatedEvent(self._hdop))

        elif t == "VFR_HUD":
            self._speed = msg.groundspeed
            EventBus.publish(SpeedUpdatedEvent(self._speed))

        elif t == "HEARTBEAT":
            try:
                mode_map = self.master.mode_mapping()
                custom_mode = msg.custom_mode
                self._mode = next((name for name, code in mode_map.items() if code == custom_mode),
                                  f"Bilinmeyen ({custom_mode})")
            except Exception as e:
                print(f"[WARN] Mode çözümleme hatası: {e}")
                self._mode = f"Bilinmeyen ({msg.custom_mode})"

            EventBus.publish(ModeUpdatedEvent(self._mode))

            self._state.update_mode(self._mode)
            self._state.update_armed(msg.base_mode)

        elif t == "COMMAND_ACK":
            try:
                EventBus.publish(CommandAckReceivedEvent(
                    command_id=msg.command,
                    result=msg.result
                ))
            except Exception as e:
                print(f"[WARN] COMMAND_ACK event yayını başarısız: {e}")
