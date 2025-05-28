# ui/map_display_adapter.py
import pathlib

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os

class MapDisplayAdapter(QWebEngineView):
    """OpenLayers haritasını yükler; GUI katmanından bağımsızdır."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # ↘︎  kök dizin =  …/gcs/
        root_dir = pathlib.Path(__file__).resolve().parent.parent
        html_path = (root_dir / "resources" / "map" / "map.html").resolve()

        print("[MAP] HTML path :", html_path)
        print("[MAP] Exists?   :", html_path.exists())

        self.load(QUrl.fromLocalFile(os.path.abspath(html_path)))
        self.setContextMenuPolicy(0)        # Sağ-tık menüsü kapalı

    def push_position_json(self, json_str: str):
        # Gelecek adımda QWebChannel'a taşıyacağız; şimdilik JS console'unda görelim
        self.page().runJavaScript(f"console.log('POINT', {json_str});")
