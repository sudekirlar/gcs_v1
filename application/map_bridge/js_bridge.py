# application/map_bridge/js_bridge.py
import json
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSlot

# Proje kökünü bulmak için:
BASE_DIR = Path(__file__).resolve().parents[2]
# resources/map/json klasörü
PLAN_DIR = BASE_DIR / "resources" / "map" / "json"
# Eğer klasör yoksa yarat
PLAN_DIR.mkdir(parents=True, exist_ok=True)
# JSON dosyasının tam yolu
PLAN_PATH = PLAN_DIR / "mission_plan.json"

class JsBridge(QObject):
    @pyqtSlot(str)
    def saveWaypoint(self, json_str: str):
        data = {"version": 1, "waypoints": []}
        if PLAN_PATH.exists():
            data = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
        wp = json.loads(json_str)
        data.setdefault("waypoints", []).append(wp)
        PLAN_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @pyqtSlot()
    def removeWaypoint(self):
        if not PLAN_PATH.exists():
            return
        data = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
        wps = data.get("waypoints", [])
        if wps:
            wps.pop()
            data["waypoints"] = wps
            PLAN_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
