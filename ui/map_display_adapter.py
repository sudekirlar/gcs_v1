# ui/map_display_adapter.py

import json, pathlib
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os

class MapDisplayAdapter(QWebEngineView):
    """OpenLayers haritasını yükler; GUI katmanından bağımsızdır."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._page_ready = False
        self._queue = []  # bekleyen JS komutları
        self.loadFinished.connect(self._on_load_finished)

        # ↘︎  kök dizin =  …/gcs/
        root_dir = pathlib.Path(__file__).resolve().parent.parent
        html_path = (root_dir / "resources" / "map" / "map.html").resolve()

        print("[MAP] HTML path :", html_path)
        print("[MAP] Exists?   :", html_path.exists())

        self.load(QUrl.fromLocalFile(os.path.abspath(html_path)))
        self.setContextMenuPolicy(0)        # Sağ-tık menüsü kapalı

    def _on_load_finished(self, ok: bool):
        self._page_ready = ok
        for cmd in self._queue:
            self.page().runJavaScript(cmd)
        self._queue.clear()

    def _emit_js(self, cmd: str):
        if self._page_ready:
            print("[MAP] JS >", cmd[:60])  # ◀︎ ekle
            self.page().runJavaScript(cmd)
        else:
            self._queue.append(cmd)

    def push_position_json(self, json_str: str):
        try:
            d = json.loads(json_str)
            lat, lon, yaw = d["latitude"], d["longitude"], d["yaw"]
        except (KeyError, json.JSONDecodeError):
            print("[MAP] Bad JSON:", json_str);
            return
        self._emit_js(f"updatePose({lat}, {lon}, {yaw});")
