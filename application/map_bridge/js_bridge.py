# application/map_bridge/js_bridge.py
from PyQt5.QtCore import QObject, pyqtSlot

class JsBridge(QObject):
    """
    Harita tarafındaki 'pushWaypointJSON' ve 'pushWaypointRemoveJSON'
    çağrılarını alıyor ama artık hiçbir dosya işlemi yapmıyor.
    JSON klasörü/​dosyası oluşturulmaması için PLAN_DIR.mkdir satırı tamamen silindi.
    """

    @pyqtSlot(str)
    def saveWaypoint(self, json_str: str):
        # Komple devre dışı bıraktık; hiçbir şey yazmıyor.
        return

    @pyqtSlot()
    def removeWaypoint(self):
        # Komple devre dışı bıraktık; hiçbir şey silmiyor.
        return
