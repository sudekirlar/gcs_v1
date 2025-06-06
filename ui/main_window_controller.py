# ui/main_window_controller.py
from pathlib import Path

from PyQt5.QtWidgets import QMessageBox, QPushButton
from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal, QTimer

from application.controller.connection_controller import ConnectionController
from application.controller.telemetry_controller import TelemetryController
from application.services.position_stream_builder import PositionStreamBuilder

from core.command.arm_command import ArmCommand
from core.command.disarm_command import DisarmCommand
from core.command.set_mode_command import SetModeCommand
from core.command.takeoff_command import TakeoffCommand
from application.workers.command_runner_worker import CommandRunnerWorker

from core.events.connection_events import ConnectionOpenedEvent, ConnectionClosedEvent, ConnectionFailedEvent
from utils.event_bus import EventBus
from utils.event_dispatcher import EventDispatcher
from core.events.telemetry_events import (
    TelemetryDataEvent,
    YawPitchRollUpdatedEvent, GPSUpdatedEvent,
    SpeedUpdatedEvent, HDOPUpdatedEvent, ModeUpdatedEvent, PositionPointReadyEvent
)
from core.events.command_events import CommandAckReceivedEvent
from core.command.land_command import LandCommand
from ui.map_display_adapter import MapDisplayAdapter

# test imports
import itertools
import json
import math

class MainWindowController(QObject):
    gui_notify = pyqtSignal(str)  # ✅ Thread-safe GUI güncellemesi için sinyal

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.connection_controller = ConnectionController()
        self.telemetry_controller = TelemetryController()
        self.thread_pool = QThreadPool.globalInstance()

        # Dispatcher
        self.dispatcher = EventDispatcher()

        # Dispatcher'dan gelen sinyalleri GUI'ye bağla
        self.dispatcher.connectionOpened.connect(self.on_connection_opened)
        self.dispatcher.connectionClosed.connect(self.on_connection_closed)
        self.dispatcher.connectionFailed.connect(self.on_connection_failed)

        self.dispatcher.yawPitchRollUpdated.connect(self.update_attitude_ui)
        self.dispatcher.gpsUpdated.connect(self.update_gps_ui)
        self.dispatcher.speedUpdated.connect(self.update_speed_ui)
        self.dispatcher.hdopUpdated.connect(self.update_hdop_ui)
        self.dispatcher.modeUpdated.connect(self.update_mode_ui)
        self.dispatcher.commandAckReceived.connect(self.on_command_ack)

        # EventBus abonelikleri
        EventBus.subscribe(ConnectionOpenedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(ConnectionClosedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(ConnectionFailedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(TelemetryDataEvent, self.dispatcher.dispatch)
        EventBus.subscribe(YawPitchRollUpdatedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(GPSUpdatedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(SpeedUpdatedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(HDOPUpdatedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(ModeUpdatedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(CommandAckReceivedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(PositionPointReadyEvent, self.dispatcher.dispatch)

        # Thread-safe GUI mesajı için sinyali bağla
        self.gui_notify.connect(self.ui.currentState_textEdit_2.setText)

        # Başlangıç durumu
        self.notify_user("Bağlantı kapalı.")
        self.refresh_port_list()

        # Buton olayları
        self.ui.openTelemetry_pushButton.clicked.connect(self.handle_open_connection)
        self.ui.closeTelemetry_pushButton.clicked.connect(self.handle_close_connection)
        self.ui.arm_pushButton.clicked.connect(self.handle_arm_command)
        self.ui.disarm_pushButton.clicked.connect(self.handle_disarm_command)
        self.ui.changeMode_pushButton.clicked.connect(self.handle_set_mode_command)
        self.ui.takeOff_pushButton.clicked.connect(self.handle_takeoff_command)
        self.ui.land_pushButton.clicked.connect(self.handle_land_command)
        self.ui.goToFocus_pushButton.clicked.connect(self.handle_focus_button)
        self.ui.clearPath_pushButton.clicked.connect(self.handle_clear_path)
        self.ui.addMarker_pushButton.clicked.connect(self.handle_add_marker)
        self.ui.clearMarker_pushButton.clicked.connect(self.handle_clear_markers)

        # Harita widget’ı oluştur
        self.map_widget = MapDisplayAdapter(parent=self.ui.centralwidget)

        # mapShown_label ile aynı konuma yerleştir
        geom = self.ui.mapShown_label.geometry()
        self.map_widget.setGeometry(geom)

        # Eski label’ı gizle
        self.ui.mapShown_label.setVisible(False)

        self.position_builder = PositionStreamBuilder()


        self.dispatcher.positionPointReady.connect(
            self.map_widget.push_position_json)

        base_dir = Path(__file__).resolve().parents[2]
        self.temp_mem_path = base_dir / "resources" / "map" / "temp_mem.json"
        self.temp_mem_path.parent.mkdir(parents=True, exist_ok=True)

        # “Save Mission” butonunu bağla
        try:
            self.ui.saveMission_pushButton.clicked.connect(self.handle_save_mission)
        except Exception:
            pass

        # test butonu
        # ■■■ Test Butonu: Sol alt köşede "Start Demo" ■■■
        self.startDemo_pushButton = QPushButton("Start Demo", parent=self.ui.centralwidget)
        # 10 px soldan, 10 px alttan
        height = self.ui.mapShown_label.geometry().height()
        self.startDemo_pushButton.setGeometry(10, height - 40, 100, 30)
        self.startDemo_pushButton.clicked.connect(self.handle_start_demo)

        # Demo timer ve iterator
        self.demo_timer = QTimer(self)
        self.demo_timer.setInterval(100)
        self.demo_timer.timeout.connect(self.push_demo_position)
        self.pos_iter = None

    def notify_user(self, message: str):
        """
        Arka thread'lerden çağrılabilir GUI mesajı.
        """
        print(f"[notify_user] {message}")  # opsiyonel log
        self.gui_notify.emit(message)  # Qt thread'ine sinyal gönder

    def refresh_port_list(self):
        self.ui.comPortTelemetry_comboBox.clear()
        self.ui.comPortTelemetry_comboBox.addItems(self.connection_controller.get_available_ports())

    def handle_open_connection(self):
        selected = self.ui.comPortTelemetry_comboBox.currentText()
        self.notify_user("Bağlanıyor...")

        if selected.startswith("TCP"):
            self.connection_controller.connect_tcp("127.0.0.1", 5760)
        else:
            self.connection_controller.connect_serial(selected)

    def handle_close_connection(self):
        self.telemetry_controller.stop()
        self.connection_controller.disconnect()
        self.notify_user("Bağlantı kapatıldı.")
        self.refresh_port_list()

    def on_connection_opened(self, event: ConnectionOpenedEvent):
        self.notify_user(f"Bağlantı başarıyla kuruldu: {event.identifier}")
        self.telemetry_controller.start()

    def on_connection_closed(self, event: ConnectionClosedEvent):
        self.telemetry_controller.stop()
        self.notify_user(f"Bağlantı kapandı: {event.identifier}")

    def on_connection_failed(self, event: ConnectionFailedEvent):
        self.notify_user(f"Bağlantı başarısız: {event.error}")

    def update_attitude_ui(self, event):
        self.ui.yaw_textEdit.setText(f"{event.yaw:.3f}")
        self.ui.pitch_textEdit.setText(f"{event.pitch:.3f}")
        self.ui.roll_textEdit.setText(f"{event.roll:.3f}")

    def update_gps_ui(self, event):
        self.ui.latitude_textEdit_2.setText(f"{event.latitude:.6f}")
        self.ui.longitude_textEdit.setText(f"{event.longitude:.6f}")
        self.ui.altitude_textEdit.setText(f"{event.altitude:.1f}")

    def update_speed_ui(self, event):
        self.ui.speed_textEdit.setText(f"{event.speed:.3f}")

    def update_hdop_ui(self, event):
        self.ui.hdop_textEdit.setText(f"{event.hdop:.2f}")

    def update_mode_ui(self, event):
        self.ui.currentMode_textEdit.setText(str(event.mode))

    # ------------------------------------------
    # KOMUT BAĞLANTILARI
    # ------------------------------------------

    def handle_arm_command(self):
        self.thread_pool.start(CommandRunnerWorker(ArmCommand(self.notify_user)))

    def handle_disarm_command(self):
        self.thread_pool.start(CommandRunnerWorker(DisarmCommand(self.notify_user)))

    def handle_set_mode_command(self):
        mode = self.ui.mode_comboBox.currentText().strip()
        if not mode:
            self.notify_user("[Uyarı] Lütfen bir uçuş modu seçiniz.")
            return
        self.thread_pool.start(CommandRunnerWorker(SetModeCommand(mode, self.notify_user)))

    def handle_takeoff_command(self):
        try:
            altitude = float(self.ui.altitudeLineEdit.text())
        except ValueError:
            self.notify_user("[Hata] Geçerli bir yükseklik değeri giriniz.")
            return
        self.thread_pool.start(CommandRunnerWorker(TakeoffCommand(altitude, self.notify_user)))

    def handle_land_command(self):
        self.thread_pool.start(CommandRunnerWorker(LandCommand(self.notify_user)))

    def on_command_ack(self, event):
        if event.result == 0:  # MAV_RESULT_ACCEPTED
            self.notify_user(f"[ACK] Komut {event.command_id} başarıyla alındı.")
        else:
            self.notify_user(f"[ACK] Komut {event.command_id} reddedildi. Kod: {event.result}")

    def handle_focus_button(self):
        self.map_widget.focus_on_drone()

    def handle_clear_path(self):
        """Clear Path Butonuna basılınca polyline’ı temizle."""
        self.map_widget._emit_js("clearPath();")
        self.notify_user("[Map] Path temizlendi.")

    def handle_add_marker(self):
        """Drone konumuna marker ekle."""
        self.map_widget._emit_js("addMarker();")
        self.notify_user("[Map] Marker eklendi.")

    def handle_clear_markers(self):
        """Tüm marker’ları temizle."""
        self.map_widget._emit_js("clearMarkers();")
        self.notify_user("[Map] Markerlar temizlendi.")

    def _on_map_ready(self):
        """
        Harita ve köprü (JsBridge) hazır olduğunda bu tetiklenir.
        Burada, JsBridge’ten gelen özet mesajları currentState_textEdit_2'ye ileteceğiz.
        """
        bridge = self.map_widget._bridge
        bridge.waypointUpdated.connect(self._on_waypoint_updated)
        print("[MainWindowController] mapReady alındı. JsBridge sinyali bağlandı.")
        self.notify_user("Harita hazır, WP işlemleri dinleniyor.")

    def _on_waypoint_updated(self, msg: str):
        """
        JsBridge’in waypointUpdated(msg) sinyalini burda yakala.
        msg örneği: "Eklendi: (37.06, 35.35) ─ Toplam: 3" veya "Silindi: (...)"
        """
        self.notify_user(msg)

    def handle_save_mission(self):
        """
        temp_mem.json dosyasını baştan "{ 'waypoints': [] }" ile yazar.
        """
        empty = {"waypoints": []}
        try:
            with open(self.temp_mem_path, "w", encoding="utf-8") as f:
                json.dump(empty, f, indent=2, ensure_ascii=False)
            print(f"[MainWindowController][DEBUG] temp_mem.json sıfırlandı (Save Mission).")
            self.notify_user("Geçici WP belleği temizlendi (Save Mission).")
        except Exception as e:
            print(f"[MainWindowController][ERROR] Save Mission temizleme hatası: {e}")
            self.notify_user("[Hata] Save Mission sırasında temp_mem temizlenemedi.")

    # test funcs
    def map_position_handler(self, event):
        # Dispatcher çağrısıyla gelen poz JSON'u direkt JS'e ilet
        pkt = json.dumps({
            'latitude': event.latitude,
            'longitude': event.longitude,
            'yaw': event.yaw
        })
        self.map_widget.push_position_json(pkt)

    def handle_start_demo(self):
        """Start Demo butonuna basılınca fake JSON üretimi başlat."""
        self.pos_iter = self._gen_positions()
        self.map_widget.enable_auto_follow()
        self.demo_timer.start()
        self.notify_user("[Demo] Başladı")

    def push_demo_position(self):
        if not self.pos_iter:
            return
        lat, lon, yaw = next(self.pos_iter)
        pkt = json.dumps({'latitude': lat, 'longitude': lon, 'yaw': yaw})
        self.map_widget.push_position_json(pkt)

    def _gen_positions(self):
        CENTER_LAT = 37.06257608177816
        CENTER_LON = 35.35287244257858
        RADIUS = 0.0005
        for t in itertools.count():
            theta = (t * 2 * math.pi) / 600
            lat = CENTER_LAT + RADIUS * math.sin(theta)
            lon = CENTER_LON + RADIUS * math.cos(theta)
            yaw = (theta * 180 / math.pi + 90) % 360
            yield lat, lon, yaw
