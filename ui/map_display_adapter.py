import json
import pathlib
import os

from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl
from application.map_bridge.js_bridge import JsBridge

class MapDisplayAdapter(QWebEngineView):
    """OpenLayers haritasını yükler; GUI katmanından bağımsızdır."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # WebEngine ayarları: JS ve yerel dosya erişimini aktifleştir
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

        self._page_ready = False
        self._queue = []  # Bekleyen JS komutları
        self.loadFinished.connect(self._on_load_finished)

        # ↘︎  kök dizin =  …/gcs/
        root_dir = pathlib.Path(__file__).resolve().parent.parent
        html_path = (root_dir / "resources" / "map" / "map.html").resolve()

        print("[MAP] HTML path :", html_path)
        print("[MAP] Exists?   :", html_path.exists())

        self.load(QUrl.fromLocalFile(os.path.abspath(html_path)))
        # Sağ-tık menüsünü geçici olarak açılabilir bırakın, debug için inspect desteği
        # self.setContextMenuPolicy(0)  # Sağ-tık menüsü kapalı

        # WebChannel kurulumunu loadFinished’ın hemen ardından yapalım
        self._channel = QWebChannel(self.page())
        self._bridge = JsBridge()
        self._channel.registerObject("bridge", self._bridge)
        self.page().setWebChannel(self._channel)

    def _on_load_finished(self, ok: bool):
        self._page_ready = ok
        for cmd in self._queue:
            self.page().runJavaScript(cmd)
        self._queue.clear()

    def _emit_js(self, cmd: str):
        if self._page_ready:
            print("[MAP] JS >", cmd[:60])
            self.page().runJavaScript(cmd)
        else:
            self._queue.append(cmd)

    def push_position_json(self, json_str: str):
        try:
            d = json.loads(json_str)
            lat, lon, yaw = d["latitude"], d["longitude"], d["yaw"]
        except (KeyError, json.JSONDecodeError):
            print("[MAP] Bad JSON:", json_str)
            return
        # JS tarafında updatePose çağrısı
        self._emit_js(f"updatePose({lat}, {lon}, {yaw});")

    def focus_on_drone(self):
        """Kullanıcı butona basınca tekrar auto-follow başlat ve odakla."""
        self._emit_js("enableAutoFollowAndFocus();")

    def enable_auto_follow(self):
        """Dinamik zoom'u yeniden etkinleştir."""
        self._emit_js("enableAutoFollowAndFocus();")

    def disable_auto_follow(self):
        """Dinamik zoom'u devre dışı bırak."""
        self._emit_js("disableAutoFollow();")