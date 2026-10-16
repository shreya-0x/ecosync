/**
 * ECOSYNC — Portal Canvas Engineering
 * Adapted from the Planet Jumping cinematic specification:
 * - Fixed full-viewport canvas
 * - Rounded-rectangle portal with corner point sampling (~10 steps per corner)
 * - Screen-locked media rendering with cover aspect ratio
 * - Fake 3D perspective with focal length ~850
 * - Smooth rotational interpolation
 * - Cubic easing full-screen transition expansion
 * - Device pixel ratio handling & responsive alignment
 */

class MaterialPortalCanvas {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext("2d");

    this.width = window.innerWidth;
    this.height = window.innerHeight;
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);

    // Current scene media
    this.currentMedia = null;
    this.mediaType = "image"; // 'image' or 'video'

    // Scene definitions
    this.scenes = [
      {
        id: "materials",
        title: "MATERIALS",
        portalImgSrc: "/static/images/cinematic/scene_materials_portal.jpg",
        bgImgSrc: "/static/images/cinematic/scene_materials_bg.jpg",
        caption: "INSPECTION APERTURE // RECYCLED POLYMERS & METALS"
      },
      {
        id: "intelligence",
        title: "INTELLIGENCE",
        portalImgSrc: "/static/images/cinematic/scene_intelligence_portal.jpg",
        bgImgSrc: "/static/images/cinematic/scene_intelligence_bg.jpg",
        caption: "SORTING CONVEYOR // YOLO COMPUTER VISION MATRIX"
      },
      {
        id: "circularity",
        title: "CIRCULARITY",
        portalImgSrc: "/static/images/cinematic/scene_circularity_portal.jpg",
        bgImgSrc: "/static/images/cinematic/scene_circularity_bg.jpg",
        caption: "REMANUFACTURING // SECONDARY RAW MATERIAL"
      }
    ];

    this.currentSceneIndex = 0;
    this.loadedImages = {};

    // Fake 3D perspective & rotation
    this.focalLength = 850;
    this.tiltX = 0;
    this.tiltY = 0;
    this.targetTiltX = 0;
    this.targetTiltY = 0;
    this.maxRotationDeg = 14;

    // Portal geometry (normalized / responsive)
    this.portalRect = { x: 0, y: 0, w: 0, h: 0, radius: 24 };
    this.expansionProgress = 0; // 0 = resting window, 1 = full viewport
    this.isExpanding = false;
    this.isTransitioning = false;

    this.init();
  }

  init() {
    this.resize();
    window.addEventListener("resize", () => this.resize());

    // Preload scene media
    this.preloadSceneAssets();

    // Mouse pointer interaction for 3D perspective
    window.addEventListener("mousemove", (e) => this.onPointerMove(e));
    window.addEventListener("mouseleave", () => this.onPointerLeave());

    // Click on canvas to expand portal into the operational platform
    this.canvas.addEventListener("click", () => {
      if (!this.isTransitioning) {
        this.triggerFullscreenExpansion();
      }
    });

    // Start animation loop
    this.render = this.render.bind(this);
    requestAnimationFrame(this.render);
  }

  preloadSceneAssets() {
    this.scenes.forEach((scene) => {
      const img = new Image();
      img.src = scene.portalImgSrc;
      img.onload = () => {
        this.loadedImages[scene.id] = img;
        if (this.scenes[this.currentSceneIndex].id === scene.id) {
          this.currentMedia = img;
        }
      };
      // Fallback handling
      img.onerror = () => {
        console.warn(`Could not load media for ${scene.id}, using fallback canvas pattern.`);
      };
    });
  }

  resize() {
    this.width = window.innerWidth;
    this.height = window.innerHeight;
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);

    this.canvas.width = this.width * this.dpr;
    this.canvas.height = this.height * this.dpr;
    this.ctx.scale(this.dpr, this.dpr);

    this.calculatePortalRestingBounds();
  }

  calculatePortalRestingBounds() {
    // Architectural dimensions: centered responsive rounded rectangle
    let portalW, portalH;

    if (this.width >= 1200) {
      portalW = Math.min(this.width * 0.44, 620);
      portalH = portalW * 1.15;
    } else if (this.width >= 768) {
      portalW = Math.min(this.width * 0.58, 480);
      portalH = portalW * 1.18;
    } else {
      portalW = this.width * 0.82;
      portalH = portalW * 1.25;
    }

    const portalX = (this.width - portalW) / 2;
    const portalY = (this.height - portalH) / 2 + 10;

    this.restingRect = {
      x: portalX,
      y: portalY,
      w: portalW,
      h: portalH,
      radius: 24
    };
  }

  onPointerMove(e) {
    // Disable on touch / coarse devices
    if (window.matchMedia("(pointer: coarse)").matches) return;

    // Pointer coordinates relative to center
    const normX = (e.clientX / this.width) * 2 - 1; // -1 to 1
    const normY = (e.clientY / this.height) * 2 - 1;

    // Horizontal pointer position influences vertical rotation; vertical influences horizontal
    this.targetTiltY = normX * this.maxRotationDeg;
    this.targetTiltX = -normY * this.maxRotationDeg;
  }

  onPointerLeave() {
    this.targetTiltX = 0;
    this.targetTiltY = 0;
  }

  setScene(index) {
    if (index < 0 || index >= this.scenes.length) return;
    this.currentSceneIndex = index;
    const scene = this.scenes[index];
    this.currentMedia = this.loadedImages[scene.id] || null;
  }

  /**
   * Reference cubic easing:
   * t < 0.5 ? 4t³ : 1 - ((-2t + 2)³ / 2)
   */
  cubicEaseInOut(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  triggerFullscreenExpansion(onComplete) {
    if (this.isTransitioning) return;
    this.isTransitioning = true;
    this.isExpanding = true;

    // Notify cinematic controller to blur surrounding UI
    document.body.classList.add("portal-expanding");

    const startTime = performance.now();
    const duration = 1100; // ms

    const animateExpansion = (currentTime) => {
      const elapsed = currentTime - startTime;
      const rawProgress = Math.min(elapsed / duration, 1.0);
      this.expansionProgress = this.cubicEaseInOut(rawProgress);

      // Interpolate tilt towards neutral 0
      this.targetTiltX = 0;
      this.targetTiltY = 0;

      if (rawProgress < 1.0) {
        requestAnimationFrame(animateExpansion);
      } else {
        this.expansionProgress = 1.0;
        this.isExpanding = false;

        // Transition into the platform view
        if (window.cinematicController) {
          window.cinematicController.commitPlatformState();
        }

        // Reopen / hide portal canvas gracefully
        setTimeout(() => {
          this.canvas.style.display = "none";
          this.isTransitioning = false;
          if (onComplete) onComplete();
        }, 350);
      }
    };

    requestAnimationFrame(animateExpansion);
  }

  /**
   * Constructs the rounded-rectangle path using sampled points
   * around all four corners (~10 sampling steps per corner).
   */
  drawSampledRoundedRect(ctx, x, y, w, h, r) {
    const steps = 10;
    const maxRadius = Math.min(r, w / 2, h / 2);

    ctx.beginPath();

    // Top-left corner to Top-right corner
    ctx.moveTo(x + maxRadius, y);
    ctx.lineTo(x + w - maxRadius, y);

    // Top-right corner arc sampled
    for (let i = 1; i <= steps; i++) {
      const angle = -Math.PI / 2 + (i / steps) * (Math.PI / 2);
      ctx.lineTo(
        x + w - maxRadius + Math.cos(angle) * maxRadius,
        y + maxRadius + Math.sin(angle) * maxRadius
      );
    }

    // Right edge to Bottom-right corner
    ctx.lineTo(x + w, y + h - maxRadius);
    for (let i = 1; i <= steps; i++) {
      const angle = (i / steps) * (Math.PI / 2);
      ctx.lineTo(
        x + w - maxRadius + Math.cos(angle) * maxRadius,
        y + h - maxRadius + Math.sin(angle) * maxRadius
      );
    }

    // Bottom edge to Bottom-left corner
    ctx.lineTo(x + maxRadius, y + h);
    for (let i = 1; i <= steps; i++) {
      const angle = Math.PI / 2 + (i / steps) * (Math.PI / 2);
      ctx.lineTo(
        x + maxRadius + Math.cos(angle) * maxRadius,
        y + h - maxRadius + Math.sin(angle) * maxRadius
      );
    }

    // Left edge to Top-left corner
    ctx.lineTo(x, y + maxRadius);
    for (let i = 1; i <= steps; i++) {
      const angle = Math.PI + (i / steps) * (Math.PI / 2);
      ctx.lineTo(
        x + maxRadius + Math.cos(angle) * maxRadius,
        y + maxRadius + Math.sin(angle) * maxRadius
      );
    }

    ctx.closePath();
  }

  render() {
    // Smooth rotational interpolation (lerp ~0.08)
    this.tiltX += (this.targetTiltX - this.tiltX) * 0.08;
    this.tiltY += (this.targetTiltY - this.tiltY) * 0.08;

    this.ctx.clearRect(0, 0, this.width, this.height);

    if (!this.restingRect) {
      requestAnimationFrame(this.render);
      return;
    }

    // Compute live interpolated portal rectangle
    const progress = this.expansionProgress;
    const currentX = this.restingRect.x * (1 - progress);
    const currentY = this.restingRect.y * (1 - progress);
    const currentW = this.restingRect.w + (this.width - this.restingRect.w) * progress;
    const currentH = this.restingRect.h + (this.height - this.restingRect.h) * progress;
    const currentRadius = this.restingRect.radius * (1 - progress);

    this.ctx.save();

    // Fake 3D perspective transform
    // Apply center pivot
    const centerX = this.width / 2;
    const centerY = this.height / 2;

    this.ctx.translate(centerX, centerY);

    // Apply rotation only when not fully expanded
    if (progress < 0.98) {
      const radX = (this.tiltX * (1 - progress) * Math.PI) / 180;
      const radY = (this.tiltY * (1 - progress) * Math.PI) / 180;

      // Matrix skew & scale simulation of perspective projection (focal length ~850)
      const perspScale = this.focalLength / (this.focalLength + 50);
      this.ctx.transform(
        perspScale * Math.cos(radY),
        Math.sin(radX) * 0.12,
        Math.sin(radY) * 0.12,
        perspScale * Math.cos(radX),
        0,
        0
      );
    }

    this.ctx.translate(-centerX, -centerY);

    // Clip to rounded-rectangle aperture
    this.drawSampledRoundedRect(
      this.ctx,
      currentX,
      currentY,
      currentW,
      currentH,
      currentRadius
    );
    this.ctx.clip();

    // Render screen-locked media behind moving portal (Cover aspect ratio)
    if (this.currentMedia && this.currentMedia.complete && this.currentMedia.naturalWidth > 0) {
      const mediaW = this.currentMedia.naturalWidth;
      const mediaH = this.currentMedia.naturalHeight;

      // Full-viewport cover math
      const scale = Math.max(this.width / mediaW, this.height / mediaH);
      const drawW = mediaW * scale;
      const drawH = mediaH * scale;
      const drawX = (this.width - drawW) / 2;
      const drawY = (this.height - drawH) / 2;

      this.ctx.drawImage(this.currentMedia, drawX, drawY, drawW, drawH);
    } else {
      // Fallback rich technical pattern if media image is still loading
      this.ctx.fillStyle = "#121815";
      this.ctx.fillRect(currentX, currentY, currentW, currentH);
      this.ctx.fillStyle = "#86efac";
      this.ctx.font = "12px monospace";
      this.ctx.fillText("ECOSYNC // OPTICAL APERTURE LOADING...", currentX + 30, currentY + 50);
    }

    // Portal Inner Border & Fine Technical Markers
    this.ctx.restore();

    if (progress < 0.95) {
      this.ctx.save();
      this.ctx.translate(centerX, centerY);
      const radX = (this.tiltX * (1 - progress) * Math.PI) / 180;
      const radY = (this.tiltY * (1 - progress) * Math.PI) / 180;
      const perspScale = this.focalLength / (this.focalLength + 50);
      this.ctx.transform(
        perspScale * Math.cos(radY),
        Math.sin(radX) * 0.12,
        Math.sin(radY) * 0.12,
        perspScale * Math.cos(radX),
        0,
        0
      );
      this.ctx.translate(-centerX, -centerY);

      // Fine border
      this.drawSampledRoundedRect(
        this.ctx,
        currentX,
        currentY,
        currentW,
        currentH,
        currentRadius
      );
      this.ctx.strokeStyle = "rgba(134, 239, 172, 0.4)";
      this.ctx.lineWidth = 1.5;
      this.ctx.stroke();

      // Technical corner brackets
      this.drawCornerReticles(this.ctx, currentX, currentY, currentW, currentH);

      this.ctx.restore();
    }

    requestAnimationFrame(this.render);
  }

  drawCornerReticles(ctx, x, y, w, h) {
    const len = 14;
    ctx.strokeStyle = "rgba(255, 255, 255, 0.6)";
    ctx.lineWidth = 2;

    // Top-Left
    ctx.beginPath();
    ctx.moveTo(x - 6, y + len);
    ctx.lineTo(x - 6, y - 6);
    ctx.lineTo(x + len, y - 6);
    ctx.stroke();

    // Top-Right
    ctx.beginPath();
    ctx.moveTo(x + w + 6, y + len);
    ctx.lineTo(x + w + 6, y - 6);
    ctx.lineTo(x + w - len, y - 6);
    ctx.stroke();

    // Bottom-Left
    ctx.beginPath();
    ctx.moveTo(x - 6, y + h - len);
    ctx.lineTo(x - 6, y + h + 6);
    ctx.lineTo(x + len, y + h + 6);
    ctx.stroke();

    // Bottom-Right
    ctx.beginPath();
    ctx.moveTo(x + w + 6, y + h - len);
    ctx.lineTo(x + w + 6, y + h + 6);
    ctx.lineTo(x + w - len, y + h + 6);
    ctx.stroke();
  }
}

window.MaterialPortalCanvas = MaterialPortalCanvas;
