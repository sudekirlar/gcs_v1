import json
import pathlib
import os

from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl

from application.map_bridge.js_bridge import JsBridge


class MapDisplayAdapter(QWebEngineView):
    """OpenLayers haritasını yükler; GUI katmanından bağımsızdır."""

    # ------------------------------------------------------------------
    # INITIALISATION
    # ------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)

        # 1) WebEngine ayarları
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

        # 2) WebChannel – sayfayı yüklemeden ÖNCE kur
        self._channel = QWebChannel()
        self._bridge = JsBridge()
        self._channel.registerObject("bridge", self._bridge)
        self.page().setWebChannel(self._channel)

        # 3) HTML dosyasını yükle
        root_dir = pathlib.Path(__file__).resolve().parent.parent            # …/gcs/
        html_path = (root_dir / "resources" / "map" / "map.html").resolve()

        print("[MAP] HTML path :", html_path)
        print("[MAP] Exists?   :", html_path.exists())

        self.load(QUrl.fromLocalFile(str(html_path)))

        # 4) Sayfa hazır olana kadar JS çağrılarını kuyrukla
        self._page_ready = False
        self._queue: list[str] = []
        self.loadFinished.connect(self._on_load_finished)

        # (isteğe bağlı) Sağ-tık menüsünü kapatmak için:
        # self.setContextMenuPolicy(0)

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------
    def _on_load_finished(self, ok: bool):
        self._page_ready = ok
        if not ok:
            print("[MAP] ✖ HTML yüklenemedi")
            return

        # Kuyruktaki bekleyen JS komutlarını çalıştır
        for cmd in self._queue:
            self.page().runJavaScript(cmd)
        self._queue.clear()

    def _emit_js(self, cmd: str):
        """Sayfa hazırsa çalıştır, değilse kuyruğa al."""
        if self._page_ready:
            print("[MAP] JS >", cmd[:80])
            self.page().runJavaScript(cmd)
        else:
            self._queue.append(cmd)

    # ------------------------------------------------------------------
    # PUBLIC API  – Harici controller’ların kullanacağı çağrılar
    # ------------------------------------------------------------------
    def push_position_json(self, json_str: str):
        """`{"latitude": …, "longitude": …, "yaw": …}` > updatePose"""
        try:
            payload = json.loads(json_str)
            lat, lon, yaw = payload["latitude"], payload["longitude"], payload["yaw"]
        except (KeyError, json.JSONDecodeError):
            print("[MAP] Bad JSON:", json_str)
            return

        self._emit_js(f"updatePose({lat}, {lon}, {yaw});")

    # ---- Auto-follow & zoom helpers ----
    def focus_on_drone(self):
        """Kullanıcı manuel odaklama isterse."""
        self._emit_js("enableAutoFollowAndFocus();")

    def enable_auto_follow(self):
        """Dinamik zoom'u yeniden aktifleştir."""
        self._emit_js("enableAutoFollowAndFocus();")

    def disable_auto_follow(self):
        """Dinamik zoom'u devre dışı bırak."""
        self._emit_js("disableAutoFollow();")
