// resources/map/dynamicZoomController.js

export class DynamicZoomController {
  constructor(map, pathLine, view, options = {}) {
    this.map       = map;
    this.pathLine  = pathLine;
    this.view      = view;
    this.autoFollow = true;
    this.padding    = options.padding  || [50,50,50,50];
    this.maxZoom    = options.maxZoom  || 18;
    this.duration   = options.duration || 300;
    this._lastFitTs = 0;
    this._throttleInterval = options.throttleInterval || 300;

    // Manuel hareket algılayıcıları
    map.on('movestart', evt => {
      if (evt.originalEvent) this.disable();
    });
    view.on('change:resolution', () => this.disable());
    map.getViewport().addEventListener('pointerdown', () => this.disable());
  }

  enable() {
    this.autoFollow = true;
    this._fitPath();
  }

  disable() {
    this.autoFollow = false;
  }

  update(coord) {
    // Drone konumunu gösterme, JS tarafı zaten yapıyor
    if (!this.autoFollow) return;
    this._throttledFit();
  }

  _throttledFit() {
    const now = Date.now();
    if (now - this._lastFitTs >= this._throttleInterval) {
      this._fitPath();
      this._lastFitTs = now;
    }
  }

  _fitPath() {
    if (!this.pathLine.getCoordinates().length) return;
    this.view.fit(this.pathLine, {
      padding : this.padding,
      maxZoom : this.maxZoom,
      duration: this.duration
    });
  }
}
