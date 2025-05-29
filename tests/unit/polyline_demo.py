# polyline_demo.py
import sys, json, math, itertools, time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore    import QTimer
from ui.map_display_adapter import MapDisplayAdapter

#  ❖ 1 – Uygulama + widget
app   = QApplication(sys.argv)
win   = QWidget()
win.setWindowTitle("Map Polyline Demo")
layout = QVBoxLayout(win)
map_w  = MapDisplayAdapter(parent=win)   # mevcut HTML'i yükler
layout.addWidget(map_w)
win.resize(800, 600)
win.show()

#  ❖ 2 – Sentetik pozisyon üreticisi
CENTER_LAT = 37.06257608177816
CENTER_LON = 35.35287244257858
RADIUS_DEG = 0.0005          # ≈ 55 m
DELAY_MS   = 100             # 10 Hz

def gen_positions():
    """sonsuz döngü: dakika başına 1 tur (yaklaşık)"""
    for t in itertools.count():
        theta = (t * 2*math.pi) / 600   # 600 adım ≈ 60 s
        lat   = CENTER_LAT + RADIUS_DEG * math.sin(theta)
        lon   = CENTER_LON + RADIUS_DEG * math.cos(theta)
        yaw   = (theta * 180 / math.pi + 90) % 360   # dik uçuş yönü
        yield lat, lon, yaw

pos_iter = gen_positions()

#  ❖ 3 – Her timer tick'inde JSON bas
def push_next():
    try:
        lat, lon, yaw = next(pos_iter)
    except StopIteration:
        return
    pkt = json.dumps(dict(latitude=lat, longitude=lon, yaw=yaw))
    map_w.push_position_json(pkt)

timer = QTimer()
timer.timeout.connect(push_next)
timer.start(DELAY_MS)

sys.exit(app.exec_())
