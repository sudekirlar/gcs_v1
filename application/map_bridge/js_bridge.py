# application/map_bridge/js_bridge.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from pathlib import Path
import json


class JsBridge(QObject):
    """
    Harita tarafındaki 'pushWaypointJSON' ve 'pushWaypointRemoveJSON'
    çağrılarını alıyor. Bu versiyonda, temp_mem.json dosyasını doğrudan kendisi güncelliyor.
    Ardından sadece UI güncellemesi için sinyal emit ediyor.
    """
    # UI’da basacağımız özet mesajlar için:
    waypointUpdated = pyqtSignal(str)  # Örnek: "Eklendi: (lat, lon) ─ Toplam: N", veya "Silindi: ..."

    def __init__(self):
        super().__init__()

        # temp_mem.json dosyasının yolu (proje kökünü baz alalım)
        base_dir = Path(__file__).resolve().parents[2]
        self.temp_mem_path = base_dir / "resources" / "map" / "temp_mem.json"
        # Klasör yoksa oluştur
        self.temp_mem_path.parent.mkdir(parents=True, exist_ok=True)
        # Uygulama her açıldığında (bridge yaratıldığında) temp_mem.json'u boşalt:
        self._clear_temp_memory_file()

    def _clear_temp_memory_file(self):
        """
        Dosyayı "{ 'waypoints': [] }" şeklinde temizler.
        """
        empty = {"waypoints": []}
        with open(self.temp_mem_path, "w", encoding="utf-8") as f:
            json.dump(empty, f, indent=2, ensure_ascii=False)
        print(f"[JsBridge] temp_mem.json başlangıçta sıfırlandı → {self.temp_mem_path}")

    def _read_waypoints(self) -> list:
        """
        Mevcut temp_mem.json'deki waypoint listesini döner.
        Hata olursa boş liste döner.
        """
        try:
            with open(self.temp_mem_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("waypoints", [])
        except Exception as e:
            print(f"[JsBridge][ERROR] Waypoint okuma hatası: {e}")
            return []

    def _write_waypoints(self, wps: list):
        """
        'wps' listesini temp_mem.json içine yazar.
        """
        out = {"waypoints": wps}
        try:
            with open(self.temp_mem_path, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[JsBridge][ERROR] Waypoint yazma hatası: {e}")

    @pyqtSlot(str)
    def saveWaypoint(self, json_str: str):
        """
        JS: window.pushWaypointJSON(JSON.stringify({latitude:...,longitude:...}))
        çağrıldığında bu çalışır.
        1) JSON parse edilir,
        2) temp_mem.json'a eklenir,
        3) terminale detaylı debug basılır,
        4) waypointUpdated sinyali özet mesajiyla emit edilir.
        """
        print(f"[JsBridge] saveWaypoint tetiklendi: {json_str}")
        try:
            wp = json.loads(json_str)
            lat = wp["latitude"]
            lon = wp["longitude"]
        except Exception as e:
            print(f"[JsBridge][ERROR] JSON parse hatası: {e}, incoming: {json_str}")
            return

        wplist = self._read_waypoints()
        wplist.append({"latitude": lat, "longitude": lon})
        self._write_waypoints(wplist)

        # Detaylı terminal log
        print(f"[JsBridge][DEBUG] Yeni waypoint eklendi → ({lat:.6f}, {lon:.6f})")
        print(f"[JsBridge][DEBUG] Toplam waypoint sayısı: {len(wplist)}")
        print(
            f"[JsBridge][DEBUG] temp_mem.json içeriği:\n{json.dumps({'waypoints': wplist}, indent=2, ensure_ascii=False)}")

        # Kısaca UI’a özet metin gönder:
        msg = f"Eklendi: ({lat:.6f}, {lon:.6f}) ─ Toplam: {len(wplist)}"
        self.waypointUpdated.emit(msg)

    @pyqtSlot()
    def removeWaypoint(self):
        """
        JS: window.pushWaypointRemoveJSON() çağrıldığında bu çalışır.
        1) Dosyadan liste okunur,
        2) Son eleman pop edilir,
        3) temp_mem.json güncellenir,
        4) debug basılır,
        5) waypointUpdated sinyali özet mesajla emit edilir.
        """
        print(f"[JsBridge] removeWaypoint tetiklendi.")
        wplist = self._read_waypoints()
        if not wplist:
            print("[JsBridge][DEBUG] Waypoint silme: liste zaten boş.")
            self.waypointUpdated.emit("Silinecek waypoint yok.")
            return

        removed = wplist.pop()
        self._write_waypoints(wplist)

        lat = removed.get("latitude")
        lon = removed.get("longitude")
        # Detaylı terminal log
        print(f"[JsBridge][DEBUG] Son waypoint silindi → ({lat:.6f}, {lon:.6f})")
        print(f"[JsBridge][DEBUG] Kalan waypoint sayısı: {len(wplist)}")
        print(
            f"[JsBridge][DEBUG] temp_mem.json içeriği:\n{json.dumps({'waypoints': wplist}, indent=2, ensure_ascii=False)}")

        # Kısaca UI’a özet metin:
        msg = f"Silindi: ({lat:.6f}, {lon:.6f}) ─ Kalan: {len(wplist)}"
        self.waypointUpdated.emit(msg)
