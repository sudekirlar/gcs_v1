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
        JS tarafından gelen {"latitude":.., "longitude":.., "altitude":..} dizgesini
        parse eder, temp_mem.json'a ekler, detaylı log basar ve özet sinyal emit eder.
        """
        print(f"[JsBridge] saveWaypoint tetiklendi: {json_str}")
        try:
            wp = json.loads(json_str)
            lat = float(wp["latitude"])
            lon = float(wp["longitude"])
            alt = wp.get("altitude", None)
            if alt is not None:
                alt = float(alt)
        except Exception as e:
            print(f"[JsBridge][ERROR] JSON parse hatası: {e}, gelen: {json_str}")
            return

        entry = {"latitude": lat, "longitude": lon}
        if alt is not None:
            entry["altitude"] = alt

        wplist = self._read_waypoints()
        wplist.append(entry)
        self._write_waypoints(wplist)

        # Detaylı terminal log
        if alt is not None:
            print(f"[JsBridge][DEBUG] Eklendi → lat: {lat:.6f}, lon: {lon:.6f}, alt: {alt:.2f} m")
        else:
            print(f"[JsBridge][DEBUG] Eklendi → lat: {lat:.6f}, lon: {lon:.6f}")
        print(f"[JsBridge][DEBUG] Toplam waypoint sayısı: {len(wplist)}")
        print(f"[JsBridge][DEBUG] temp_mem.json içeriği:\n"
              f"{json.dumps({'waypoints': wplist}, indent=2, ensure_ascii=False)}")

        # Özet mesajı emit et
        if alt is not None:
            msg = f"Eklendi: ({lat:.6f}, {lon:.6f}, {alt:.1f} m) ─ Toplam: {len(wplist)}"
        else:
            msg = f"Eklendi: ({lat:.6f}, {lon:.6f}) ─ Toplam: {len(wplist)}"
        self.waypointUpdated.emit(msg)

    @pyqtSlot()
    def removeWaypoint(self):
        """
        JS: window.pushWaypointRemoveJSON() çağrıldığında
        temp_mem.json'dan son waypoint'i çıkarır, log basar, özet sinyal emit eder.
        """
        print(f"[JsBridge] removeWaypoint tetiklendi.")
        wplist = self._read_waypoints()
        if not wplist:
            print("[JsBridge][DEBUG] Silinecek waypoint yok.")
            self.waypointUpdated.emit("Silinecek waypoint yok.")
            return

        removed = wplist.pop()
        self._write_waypoints(wplist)

        lat = removed.get("latitude")
        lon = removed.get("longitude")
        alt = removed.get("altitude", None)

        # Detaylı terminal log
        if alt is not None:
            print(f"[JsBridge][DEBUG] Silindi → lat: {lat:.6f}, lon: {lon:.6f}, alt: {alt:.2f} m")
        else:
            print(f"[JsBridge][DEBUG] Silindi → lat: {lat:.6f}, lon: {lon:.6f}")
        print(f"[JsBridge][DEBUG] Kalan waypoint sayısı: {len(wplist)}")
        print(f"[JsBridge][DEBUG] temp_mem.json içeriği:\n"
              f"{json.dumps({'waypoints': wplist}, indent=2, ensure_ascii=False)}")

        # Özet mesajı emit et
        if alt is not None:
            msg = f"Silindi: ({lat:.6f}, {lon:.6f}, {alt:.1f} m) ─ Kalan: {len(wplist)}"
        else:
            msg = f"Silindi: ({lat:.6f}, {lon:.6f}) ─ Kalan: {len(wplist)}"
        self.waypointUpdated.emit(msg)