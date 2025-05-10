# ui/main_window_controller.py

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject
from application.controller.connection_controller import ConnectionController
from application.controller.telemetry_controller import TelemetryController
from core.events.connection_events import ConnectionOpenedEvent, ConnectionClosedEvent, ConnectionFailedEvent
from utils.event_bus import EventBus
from utils.event_dispatcher import EventDispatcher  # 👈 Yeni
from core.events.telemetry_events import TelemetryDataEvent
from core.events.telemetry_events import (
    TelemetryDataEvent,
    YawPitchRollUpdatedEvent, GPSUpdatedEvent,
    SpeedUpdatedEvent, HDOPUpdatedEvent, ModeUpdatedEvent
)

class MainWindowController(QObject):
    def __init__(self, ui):
        """
        Arayüzdeki bileşenlerin kontrolünü sağlar.
        PushButton olayları burada ele alınır.
        """
        super().__init__()
        self.ui = ui
        self.connection_controller = ConnectionController()

        # Dispatcher
        self.dispatcher = EventDispatcher()

        # Dispatcher'dan gelen sinyalleri GUI'ye bağla
        self.dispatcher.connectionOpened.connect(self.on_connection_opened)
        self.dispatcher.connectionClosed.connect(self.on_connection_closed)
        self.dispatcher.connectionFailed.connect(self.on_connection_failed)

        # PushButton bağlantıları
        self.ui.openTelemetry_pushButton.clicked.connect(self.handle_open_connection)
        self.ui.closeTelemetry_pushButton.clicked.connect(self.handle_close_connection)

        # EventBus'ı GUI güvenli hale getir
        EventBus.subscribe(ConnectionOpenedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(ConnectionClosedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(ConnectionFailedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(TelemetryDataEvent, self.dispatcher.dispatch)

        # Yeni modüler telemetry event'leri
        EventBus.subscribe(YawPitchRollUpdatedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(GPSUpdatedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(SpeedUpdatedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(HDOPUpdatedEvent, self.dispatcher.dispatch)
        EventBus.subscribe(ModeUpdatedEvent, self.dispatcher.dispatch)

        # Başlangıç durumu
        self.ui.currentState_textEdit_2.setText("Bağlantı kapalı.")
        self.refresh_port_list()

        self.telemetry_controller = TelemetryController()

        # self.dispatcher.telemetryReceived.connect(self.update_telemetry_gui)
        self.dispatcher.yawPitchRollUpdated.connect(self.update_attitude_ui)
        self.dispatcher.gpsUpdated.connect(self.update_gps_ui)
        self.dispatcher.speedUpdated.connect(self.update_speed_ui)
        self.dispatcher.hdopUpdated.connect(self.update_hdop_ui)
        self.dispatcher.modeUpdated.connect(self.update_mode_ui)

    def refresh_port_list(self):
        """
        Mevcut portları liste kutusuna ekler. TCP dahil.
        """
        self.ui.comPortTelemetry_comboBox.clear()
        self.ui.comPortTelemetry_comboBox.addItems(self.connection_controller.get_available_ports())

    def handle_open_connection(self):
        """
        Kullanıcı 'Bağlan' butonuna bastığında çalışır.
        """
        selected = self.ui.comPortTelemetry_comboBox.currentText()
        self.ui.currentState_textEdit_2.setText("Bağlanıyor...")

        if selected.startswith("TCP"):
            self.connection_controller.connect_tcp("127.0.0.1", 5760)
        else:
            self.connection_controller.connect_serial(selected)

    def handle_close_connection(self):
        """
        Kullanıcı 'Bağlantıyı Kapat' butonuna bastığında çalışır.
        """
        self.telemetry_controller.stop()  # ✅ telemetry thread'i durdur
        self.connection_controller.disconnect()
        self.ui.currentState_textEdit_2.setText("Bağlantı kapatıldı.")
        self.refresh_port_list()

    def on_connection_opened(self, event: ConnectionOpenedEvent):
        self.ui.currentState_textEdit_2.setText(f"Bağlantı başarıyla kuruldu: {event.identifier}")
        self.telemetry_controller.start()

    def on_connection_closed(self, event: ConnectionClosedEvent):
        self.telemetry_controller.stop()  # ❗ güvenlik için burada da çağrılabilir
        self.ui.currentState_textEdit_2.setText(f"Bağlantı kapandı: {event.identifier}")

    def on_connection_failed(self, event: ConnectionFailedEvent):
        self.ui.currentState_textEdit_2.setText(f"Bağlantı başarısız: {event.error}")

    # def update_telemetry_gui(self, event: TelemetryDataEvent):
    #     self.ui.yaw_textEdit.setText(f"{event.yaw:.3f}")
    #     self.ui.pitch_textEdit.setText(f"{event.pitch:.3f}")
    #     self.ui.roll_textEdit.setText(f"{event.roll:.3f}")
    #     self.ui.latitude_textEdit_2.setText(f"{event.latitude:.6f}")
    #     self.ui.longitude_textEdit.setText(f"{event.longitude:.6f}")
    #     self.ui.altitude_textEdit.setText(f"{event.altitude:.1f}")
    #     self.ui.speed_textEdit.setText(f"{event.speed:.3f}")
    #     self.ui.currentMode_textEdit.setText(str(event.mode))
    #     self.ui.hdop_textEdit.setText(f"{event.hdop:.2f}")

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
