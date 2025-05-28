# ui/main_window_controller.py

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal

from application.controller.connection_controller import ConnectionController
from application.controller.telemetry_controller import TelemetryController

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
    SpeedUpdatedEvent, HDOPUpdatedEvent, ModeUpdatedEvent
)
from core.events.command_events import CommandAckReceivedEvent
from core.command.land_command import LandCommand
from ui.map_display_adapter import MapDisplayAdapter

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

        # Harita widget’ı oluştur
        self.map_widget = MapDisplayAdapter(parent=self.ui.centralwidget)

        # mapShown_label ile aynı konuma yerleştir
        geom = self.ui.mapShown_label.geometry()
        self.map_widget.setGeometry(geom)

        # Eski label’ı gizle
        self.ui.mapShown_label.setVisible(False)

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