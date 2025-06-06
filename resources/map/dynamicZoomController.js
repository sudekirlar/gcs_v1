// resources/map/dynamicZoomController.js
(function(window) {
  /**
   * Dinamik zoom ve takip kontrolörü.
   * Harita (map), çizgi (pathLine) ve view nesnelerini alır.
   */
  class DynamicZoomController {
    constructor(map, pathLine, view, options = {}) {
      this.map        = map;
      this.pathLine   = pathLine;
      this.view       = view;
      this.autoFollow = true;

      // Ayarlar
      this.padding          = options.padding       || [50,50,50,50];
      this.maxZoom          = options.maxZoom       || 18;
      this.duration         = options.duration      || 300;  // enable() için animasyon süresi
      this.fastDuration     = options.fastDuration  ?? 0;    // update() için animasyon süresi
      this.throttleInterval = options.throttleInterval || 300;

      // Durum tutucuları
      this._lastFitTs  = 0;
      this._lastExtent = null;

      // Manuel etkileşim algılayıcıları → auto-follow’u kapat
      map.on('movestart',     evt => { if (evt.originalEvent) this.disable(); });
      map.on('pointerdrag',   ()  => { this.disable(); });
      // artık zoom değişince auto-follow kapanmasın:
      // view.on('change:resolution', ()  => { this.disable(); });
      map.getViewport().addEventListener('pointerdown', () => { this.disable(); });
    }

    /**
     * Auto-follow’u açar.
     * Sadece false’dan true’ya geçişte zoom kontrolünü yapar:
     * Eğer mevcut zoom, hesaplanan zoom’la aynıysa sadece center,
     * değilse tüm path’i fit eder.
     */
    enable() {
      const wasFollowing = this.autoFollow;
      this.autoFollow = true;

      if (!wasFollowing) {
        const coords = this.pathLine.getCoordinates();
        if (!coords.length) return;

        const extent = this.pathLine.getExtent();
        const size   = this.map.getSize();
        const resExp = this.view.getResolutionForExtent(extent, size);
        const zoomExp = this.view.getZoomForResolution(resExp);
        const zoomCur = this.view.getZoom();

        if (Math.abs(zoomExp - zoomCur) < 1e-6) {
          // Zoom değişmemiş → sadece en son noktayı merkeze al
          this.view.setCenter(coords[coords.length - 1]);
        } else {
          // Zoom farklı → tüm çizgiyi sığdır
          this.view.fit(extent, {
            padding : this.padding,
            maxZoom : this.maxZoom,
            duration: this.duration
          });
          this._lastExtent = extent.slice();
          this._lastFitTs  = Date.now();
        }
      }
    }

    /** Auto-follow’u kapatır. */
    disable() {
      this.autoFollow = false;
    }

    /**
     * Her yeni koordinatta çağrılır.
     * Eğer auto-follow açıksa:
     *  - Sadece drone görünüm dışında kaldığında merkeze alır,
     *  - Extent değiştiyse ve throttle süresi dolduysa hızlı fit yapar.
     */
    update(coord) {
      if (!this.autoFollow) return;

      // 1) Sadece drone görünürde değilse merkeze al
      const viewExtent = this.view.calculateExtent(this.map.getSize());
      if (!ol.extent.containsCoordinate(viewExtent, coord)) {
        this.view.setCenter(coord);
      }

      // 2) Sadece extent değiştiyse ve throttle süresi dolduysa fit et
      const extent = this.pathLine.getExtent();
      if (!this._lastExtent || !equalExtents(extent, this._lastExtent)) {
        const now = Date.now();
        if (now - this._lastFitTs >= this.throttleInterval) {
          this.view.fit(extent, {
            padding : this.padding,
            maxZoom : this.maxZoom,
            duration: this.fastDuration
          });
          this._lastExtent = extent.slice();
          this._lastFitTs  = now;
        }
      }
    }
  }

  /** Global namespace’e sınıfı ata */
  window.DynamicZoomController = DynamicZoomController;

  /**
   * İki extent dizisini (minX, minY, maxX, maxY) yaklaşık eşitlik kriteriyle karşılaştırır.
   */
  function equalExtents(e1, e2) {
    for (let i = 0; i < 4; i++) {
      if (Math.abs(e1[i] - e2[i]) > 1e-6) return false;
    }
    return true;
  }
})(window);
