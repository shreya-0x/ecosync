/**
 * ECOSYNC — Cinematic Controller
 * Manages preloader sequence, logo docking, scene switcher, and custom cursor.
 */

class CinematicController {
  constructor() {
    this.preloader = document.getElementById("cinematic-preloader");
    this.counterEl = document.getElementById("preloader-counter-text");
    this.progressFill = document.getElementById("preloader-progress-fill");
    this.centerLogo = document.getElementById("preloader-center-logo");
    this.headerLogo = document.getElementById("header-brand-logo");
    this.skipBtn = document.getElementById("preloader-skip-btn");

    this.scenes = [
      {
        index: 0,
        number: "01 / 03",
        title: "MATERIALS",
        category: "PHYSICAL COMPOSITION",
        rows: [
          "01 / COMPOSITION: POLYMER & CELLULOSE VECTORS",
          "PURITY THRESHOLD: 94.2% OPTICAL SPECIFICATION",
          "TARGET METRIC: ZERO UNTRACKED RESIDUAL FLOW"
        ]
      },
      {
        index: 1,
        number: "02 / 03",
        title: "INTELLIGENCE",
        category: "COMPUTATIONAL RECOGNITION",
        rows: [
          "02 / COMPUTER VISION: YOLO INFERENCE ENGINE",
          "LOCALIZATION: REAL-TIME BOUNDING MATRIX",
          "MULTI-SPECTRAL: RESIN & ALLOY VERIFICATION"
        ]
      },
      {
        index: 2,
        number: "03 / 03",
        title: "CIRCULARITY",
        category: "CLOSED-LOOP TRANSFORMATION",
        rows: [
          "03 / TRACEABILITY: END-TO-END CHAIN OF CUSTODY",
          "INFRASTRUCTURE: 5 REGIONAL RECOVERY HUBS",
          "VERIFICATION: EPA WARM v15 VERIFIED IMPACT"
        ]
      }
    ];

    this.currentSceneIdx = 0;
    this.preloaderComplete = false;

    this.initCursor();
    this.initPreloader();
    this.initSceneNavigation();
  }

  initCursor() {
    const dot = document.querySelector(".cursor-dot");
    const ring = document.querySelector(".cursor-ring");
    const badge = document.querySelector(".cursor-badge");

    if (!dot || !ring || window.matchMedia("(pointer: coarse)").matches) return;

    let mouseX = -100;
    let mouseY = -100;
    let ringX = -100;
    let ringY = -100;

    window.addEventListener("mousemove", (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;

      dot.style.transform = `translate(${mouseX}px, ${mouseY}px) translate(-50%, -50%)`;
      if (badge) {
        badge.style.transform = `translate(${mouseX + 24}px, ${mouseY - 12}px)`;
      }
    });

    const updateRing = () => {
      ringX += (mouseX - ringX) * 0.2;
      ringY += (mouseY - ringY) * 0.2;
      ring.style.transform = `translate(${ringX}px, ${ringY}px) translate(-50%, -50%)`;
      requestAnimationFrame(updateRing);
    };
    requestAnimationFrame(updateRing);

    // Canvas portal hover
    const portalCanvas = document.getElementById("portal-canvas");
    if (portalCanvas) {
      portalCanvas.addEventListener("mouseenter", () => {
        document.body.classList.add("cursor-hover", "cursor-portal-hover");
      });
      portalCanvas.addEventListener("mouseleave", () => {
        document.body.classList.remove("cursor-hover", "cursor-portal-hover");
      });
    }

    // Interactive elements hover
    document.querySelectorAll("button, a, input, select").forEach((el) => {
      el.addEventListener("mouseenter", () => document.body.classList.add("cursor-hover"));
      el.addEventListener("mouseleave", () => document.body.classList.remove("cursor-hover"));
    });
  }

  initPreloader() {
    if (!this.preloader) return;

    // Skip intro if user requested reduced motion or previously visited (unless replaying)
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      this.finishPreloader();
      return;
    }

    if (this.skipBtn) {
      this.skipBtn.addEventListener("click", () => this.finishPreloader());
    }

    // Run 3-second counter
    let progress = 0;
    const duration = 2800;
    const startTime = performance.now();

    const updateCounter = (now) => {
      if (this.preloaderComplete) return;

      const elapsed = now - startTime;
      progress = Math.min((elapsed / duration) * 100, 100);

      const formatted = Math.floor(progress).toString().padStart(2, "0");
      if (this.counterEl) {
        this.counterEl.textContent = `${formatted}%`;
      }
      if (this.progressFill) {
        this.progressFill.style.width = `${progress}%`;
      }

      if (progress < 100) {
        requestAnimationFrame(updateCounter);
      } else {
        setTimeout(() => this.dockLogoAndReveal(), 200);
      }
    };

    requestAnimationFrame(updateCounter);
  }

  dockLogoAndReveal() {
    if (this.preloaderComplete) return;

    // 1. Counter blurs and moves upward
    if (this.counterEl) {
      this.counterEl.style.transition = "transform 0.6s var(--transition-smooth), opacity 0.6s, filter 0.6s";
      this.counterEl.style.transform = "translateY(-24px)";
      this.counterEl.style.filter = "blur(10px)";
      this.counterEl.style.opacity = "0";
    }

    // 2. Dock center logo to top-left header position over ~2s
    if (this.centerLogo && this.headerLogo) {
      const centerRect = this.centerLogo.getBoundingClientRect();
      const headerRect = this.headerLogo.getBoundingClientRect();

      const deltaX = headerRect.left - centerRect.left;
      const deltaY = headerRect.top - centerRect.top;
      const scale = headerRect.height / centerRect.height;

      this.centerLogo.style.transition = "transform 1.8s cubic-bezier(0.65, 0, 0.35, 1), opacity 1.8s";
      this.centerLogo.style.transformOrigin = "top left";
      this.centerLogo.style.transform = `translate(${deltaX}px, ${deltaY}px) scale(${scale})`;

      setTimeout(() => {
        this.finishPreloader();
      }, 1800);
    } else {
      this.finishPreloader();
    }
  }

  finishPreloader() {
    if (this.preloaderComplete) return;
    this.preloaderComplete = true;

    if (this.preloader) {
      this.preloader.classList.add("fade-out");
      setTimeout(() => {
        this.preloader.style.display = "none";
      }, 800);
    }

    // Reveal first scene
    this.renderScene(0);
  }

  initSceneNavigation() {
    const prevBtn = document.getElementById("btn-prev-scene");
    const nextBtn = document.getElementById("btn-next-scene");
    const exploreBtn = document.getElementById("btn-explore-platform");

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        const next = (this.currentSceneIdx - 1 + this.scenes.length) % this.scenes.length;
        this.renderScene(next);
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        const next = (this.currentSceneIdx + 1) % this.scenes.length;
        this.renderScene(next);
      });
    }

    if (exploreBtn) {
      exploreBtn.addEventListener("click", () => {
        if (window.portalCanvas) {
          window.portalCanvas.triggerFullscreenExpansion();
        } else {
          this.commitPlatformState();
        }
      });
    }
  }

  renderScene(idx) {
    this.currentSceneIdx = idx;
    const scene = this.scenes[idx];

    // Update portal canvas media
    if (window.portalCanvas) {
      window.portalCanvas.setScene(idx);
    }

    // Update background media crossfade
    document.querySelectorAll(".cinematic-bg-img").forEach((img, i) => {
      img.classList.toggle("active", i === idx);
    });

    // Update Meta and Titles
    const counterBadge = document.querySelector(".scene-counter-badge");
    const categoryPill = document.querySelector(".scene-category-pill");
    const giantTitle = document.querySelector(".giant-display-title");
    const dataRows = document.querySelectorAll(".data-row-item");

    if (counterBadge) counterBadge.textContent = scene.number;
    if (categoryPill) categoryPill.textContent = scene.category;

    if (giantTitle) {
      giantTitle.classList.remove("revealed");
      setTimeout(() => {
        giantTitle.textContent = scene.title;
        giantTitle.classList.add("revealed");
      }, 150);
    }

    // Staggered reveals for rows (Planet Jumping reference motion timings: ~0.72s each, 0.16s stagger)
    dataRows.forEach((row, i) => {
      row.classList.remove("revealed");
      if (scene.rows[i]) {
        row.textContent = scene.rows[i];
        setTimeout(() => {
          row.classList.add("revealed");
        }, 300 + i * 160);
      }
    });
  }

  commitPlatformState() {
    const heroSection = document.getElementById("cinematic-hero-section");
    const platformSection = document.getElementById("operational-platform");

    if (heroSection) heroSection.style.display = "none";
    if (platformSection) {
      platformSection.classList.add("active");
    }

    // Switch to initial platform view (Scanner or Overview)
    if (window.ecosyncApp) {
      window.ecosyncApp.switchView("scanner");
    }
  }

  replayIntro() {
    const heroSection = document.getElementById("cinematic-hero-section");
    const platformSection = document.getElementById("operational-platform");
    const portalCanvas = document.getElementById("portal-canvas");

    if (platformSection) platformSection.classList.remove("active");
    if (heroSection) heroSection.style.display = "flex";
    if (portalCanvas) {
      portalCanvas.style.display = "block";
      if (window.portalCanvas) {
        window.portalCanvas.expansionProgress = 0;
        window.portalCanvas.isTransitioning = false;
        window.portalCanvas.resize();
      }
    }

    this.renderScene(0);
  }
}

window.CinematicController = CinematicController;
