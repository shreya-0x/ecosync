/**
 * ECOSYNC — Main Application Coordinator
 * Manages view routing across Home, Scan Waste, Waste Guide, Digital Twin, My Impact, and AI Advisor.
 * Provides global toast notifications, mobile navigation, and quick item lookup.
 */

class EcoSyncApp {
  constructor() {
    this.currentView = "home";
    this.init();
  }

  init() {
    // 1. Initialize Global Toast System
    window.showEcoSyncToast = (message, type = "success") => this.showToast(message, type);

    // 2. Initialize Platform Services safely
    if (typeof WasteScanner !== "undefined" && !window.wasteScanner) {
      window.wasteScanner = new WasteScanner();
    }
    window.ecosyncScanner = window.wasteScanner;
    if (typeof WasteGuide !== "undefined" && !window.wasteGuide) window.wasteGuide = new WasteGuide();
    if (typeof DigitalTwin !== "undefined" && !window.digitalTwin) window.digitalTwin = new DigitalTwin();
    if (typeof HouseholdImpact !== "undefined" && !window.householdImpact) window.householdImpact = new HouseholdImpact();
    if (typeof AIAdvisor !== "undefined" && !window.aiAdvisor) window.aiAdvisor = new AIAdvisor();

    // 3. Navigation & Experience Setup
    this.isDemoMode = true;
    this.initTheme();
    this.initNavigation();
    this.initHomeActions();
    this.initQuickBinFinder();
    this.initDemoModeControls();
    this.initWelcomeModal();

    // 4. Fetch initial model status & health
    this.checkHealthAndModelStatus();
    this.fetchHomeLiveStats();

    // 5. Default to home view
    this.switchView("home");
  }

  initDemoModeControls() {
    const btnToggle = document.getElementById("btn-header-demo-toggle");
    const banner = document.getElementById("global-demo-banner");
    const btnText = document.getElementById("header-demo-btn-text");
    const indicator = document.getElementById("home-demo-indicator");

    const setDemoState = (active) => {
      this.isDemoMode = active;
      if (btnToggle) {
        btnToggle.classList.toggle("active", active);
        if (btnText) btnText.textContent = active ? "Demo Data: ON" : "Demo Data: OFF";
      }
      if (banner) {
        banner.style.display = active ? "flex" : "none";
      }
      if (indicator) {
        indicator.style.display = active ? "inline-block" : "none";
      }
    };
    this.setDemoState = setDemoState;

    if (btnToggle) {
      btnToggle.addEventListener("click", () => {
        setDemoState(!this.isDemoMode);
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast(this.isDemoMode ? "Demo Mode activated: Showing seeded records." : "Demo Mode turned off.");
        }
      });
    }

    const btnExit = document.getElementById("btn-exit-demo-mode");
    if (btnExit) {
      btnExit.addEventListener("click", () => {
        setDemoState(false);
        if (window.showEcoSyncToast) window.showEcoSyncToast("Demo banner hidden. Click 'Demo Data' in header anytime to re-enable.");
      });
    }

    // Walkthrough modal triggers
    const walkthroughModal = document.getElementById("walkthrough-modal");
    let currentWalkthroughStep = 0;
    const walkthroughSteps = [
      {
        title: "Step 1: Real AI Computer Vision Scanner",
        body: "EcoSync runs genuine local YOLO object inference with normalized bounding boxes, exact confidence percentages, and explicit separation of visual detection from material classification.",
        view: "scanner"
      },
      {
        title: "Step 2: Digital Twin Command Centre",
        body: "Interactive campus grid telemetry simulating waste stream flows, fill bottlenecks, and collection route efficiency under variable scenario loads.",
        view: "twin"
      },
      {
        title: "Step 3: Smart Bin Network & Dispatch",
        body: "Real-time ultrasonic fill level and battery monitoring across campus bins with one-click dispatch and servicing workflows.",
        view: "smart-bins"
      },
      {
        title: "Step 4: Circular Sustainability Advisor & Impact",
        body: "Complete 17-class zero-landfill taxonomy, verified disposal blueprints, GHG abatement metrics, and RFC-4180 verified CSV audit exports.",
        view: "impact"
      }
    ];

    const updateWalkthroughUI = () => {
      const step = walkthroughSteps[currentWalkthroughStep];
      const titleEl = document.getElementById("walkthrough-step-title");
      const bodyEl = document.getElementById("walkthrough-step-body");
      const progEl = document.getElementById("walkthrough-progress-label");
      const btnPrev = document.getElementById("btn-walkthrough-prev");
      const btnNext = document.getElementById("btn-walkthrough-next");

      if (titleEl) titleEl.textContent = step.title;
      if (bodyEl) bodyEl.textContent = step.body;
      if (progEl) progEl.textContent = `STEP ${currentWalkthroughStep + 1} OF ${walkthroughSteps.length}`;
      if (btnPrev) btnPrev.disabled = currentWalkthroughStep === 0;
      if (btnNext) {
        btnNext.textContent = currentWalkthroughStep === walkthroughSteps.length - 1 ? "Finish Tour ✓" : "Next Step →";
      }
      this.switchView(step.view);
    };

    const openWalkthrough = () => {
      currentWalkthroughStep = 0;
      updateWalkthroughUI();
      if (walkthroughModal) walkthroughModal.style.display = "flex";
    };

    const btnOpenWalkthrough = document.getElementById("btn-open-walkthrough");
    if (btnOpenWalkthrough) btnOpenWalkthrough.addEventListener("click", openWalkthrough);

    const btnHeroWalkthrough = document.getElementById("btn-hero-demo-tour");
    if (btnHeroWalkthrough) btnHeroWalkthrough.addEventListener("click", openWalkthrough);

    const btnCloseWalkthrough = document.getElementById("btn-close-walkthrough");
    if (btnCloseWalkthrough && walkthroughModal) {
      btnCloseWalkthrough.addEventListener("click", () => {
        walkthroughModal.style.display = "none";
      });
    }

    const btnPrevWalk = document.getElementById("btn-walkthrough-prev");
    if (btnPrevWalk) {
      btnPrevWalk.addEventListener("click", () => {
        if (currentWalkthroughStep > 0) {
          currentWalkthroughStep--;
          updateWalkthroughUI();
        }
      });
    }

    const btnNextWalk = document.getElementById("btn-walkthrough-next");
    if (btnNextWalk) {
      btnNextWalk.addEventListener("click", () => {
        if (currentWalkthroughStep < walkthroughSteps.length - 1) {
          currentWalkthroughStep++;
          updateWalkthroughUI();
        } else {
          if (walkthroughModal) walkthroughModal.style.display = "none";
          if (window.showEcoSyncToast) window.showEcoSyncToast("Platform tour complete! You can explore freely.");
        }
      });
    }

    if (walkthroughModal) {
      walkthroughModal.addEventListener("click", (e) => {
        if (e.target === walkthroughModal) walkthroughModal.style.display = "none";
      });
    }

    // Reset Demo Records Button
    const btnResetDemo = document.getElementById("btn-reset-demo-records");
    if (btnResetDemo) {
      btnResetDemo.addEventListener("click", async () => {
        try {
          btnResetDemo.disabled = true;
          btnResetDemo.textContent = "Resetting...";
          const resp = await fetch("/api/demo/reset", { method: "POST" });
          const res = await resp.json();
          if (res.status === "success") {
            this.fetchHomeLiveStats();
            if (window.householdImpact) {
              window.householdImpact.fetchImpactMetrics();
              window.householdImpact.fetchHistory();
            }
            if (window.digitalTwin) {
              window.digitalTwin.fetchBins();
              window.digitalTwin.fetchRoutes();
            }
            if (window.showEcoSyncToast) {
              window.showEcoSyncToast("Demo dataset successfully restored to pristine baseline!");
            }
          }
        } catch (err) {
          console.error("Error resetting demo data:", err);
        } finally {
          btnResetDemo.disabled = false;
          btnResetDemo.textContent = "🔄 Reset Demo Data";
        }
      });
    }
  }

  initNavigation() {
    // Nav links
    document.querySelectorAll(".nav-link").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const viewId = e.currentTarget.getAttribute("data-view");
        if (viewId) {
          this.switchView(viewId);
        }
        // Close mobile nav if open
        const nav = document.getElementById("main-header-nav");
        if (nav) nav.classList.remove("mobile-active");
      });
    });

    // Brand logo returns to home
    const brand = document.getElementById("header-brand-logo");
    if (brand) {
      brand.addEventListener("click", (e) => {
        e.preventDefault();
        this.switchView("home");
      });
    }

    // Direct header action buttons
    document.querySelectorAll("[data-nav-target]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const target = e.currentTarget.getAttribute("data-nav-target");
        if (target) this.switchView(target);
      });
    });

    // Mobile nav toggle
    const mobileBtn = document.getElementById("btn-mobile-menu");
    const mainNav = document.getElementById("main-header-nav");
    if (mobileBtn && mainNav) {
      mobileBtn.addEventListener("click", () => {
        mainNav.classList.toggle("mobile-active");
      });
    }

    // Floating Back to Top Button
    const btnScrollTop = document.getElementById("btn-scroll-top");
    if (btnScrollTop) {
      window.addEventListener("scroll", () => {
        btnScrollTop.classList.toggle("visible", window.scrollY > 250);
      });
      btnScrollTop.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }
  }

  initHomeActions() {
    // Hero CTA buttons
    const btnHeroScan = document.getElementById("btn-hero-scan");
    if (btnHeroScan) {
      btnHeroScan.addEventListener("click", () => {
        this.switchView("scanner");
        if (window.wasteScanner) {
          window.wasteScanner.startCamera();
        }
      });
    }

    const btnHeroGuide = document.getElementById("btn-hero-guide");
    if (btnHeroGuide) {
      btnHeroGuide.addEventListener("click", () => this.switchView("guide"));
    }

    const btnHeroTwin = document.getElementById("btn-hero-twin");
    if (btnHeroTwin) {
      btnHeroTwin.addEventListener("click", () => this.switchView("twin"));
    }
  }

  initQuickBinFinder() {
    // Connect quick item cards to waste guide
    document.querySelectorAll(".quick-item-card").forEach((card) => {
      card.addEventListener("click", (e) => {
        const itemId = e.currentTarget.getAttribute("data-quick-item");
        if (itemId && window.wasteGuide) {
          this.switchView("guide");
          const searchInput = document.getElementById("guide-search-input");
          if (searchInput) {
            // Map itemId to friendly search query
            const queries = {
              "plastic_bottle": "bottle",
              "food_scraps": "food",
              "pizza_box": "pizza",
              "aa_battery": "battery",
              "used_cooking_oil": "oil",
              "aluminum_can": "can"
            };
            searchInput.value = queries[itemId] || itemId;
            window.wasteGuide.currentQuery = searchInput.value;
            window.wasteGuide.fetchItems();
          }
        }
      });
    });
  }

  switchView(viewId) {
    this.currentView = viewId;

    // Update nav links
    document.querySelectorAll(".nav-link").forEach((link) => {
      link.classList.toggle("active", link.getAttribute("data-view") === viewId);
    });

    // Update view panels
    document.querySelectorAll(".platform-view").forEach((view) => {
      view.classList.toggle("active", view.id === `view-${viewId}`);
    });

    // View specific hooks
    if (viewId === "home") {
      this.fetchHomeLiveStats();
    } else if (viewId === "twin" && window.digitalTwin) {
      window.digitalTwin.fetchBins();
      window.digitalTwin.fetchRoutes();
    } else if (viewId === "smart-bins" && window.digitalTwin) {
      window.digitalTwin.fetchBins();
    } else if (viewId === "guide" && window.wasteGuide) {
      window.wasteGuide.fetchItems();
    } else if (viewId === "impact" && window.householdImpact) {
      window.householdImpact.fetchImpactMetrics();
      window.householdImpact.fetchHistory();
    } else if (viewId === "advisor" && window.aiAdvisor) {
      const input = document.getElementById("advisor-query-input");
      if (input) setTimeout(() => input.focus(), 150);
    } else if (viewId === "about") {
      this.checkHealthAndModelStatus();
    }

    // Smooth scroll to top of view
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async checkHealthAndModelStatus() {
    try {
      const resp = await fetch("/api/model-status");
      const data = await resp.json();
      if (data.status === "success" && data.model) {
        const m = data.model;
        const statusBadge = document.getElementById("header-model-badge");
        if (statusBadge) {
          statusBadge.textContent = m.is_loaded ? `AI MODEL: ${m.model_name}` : "MODEL: STANDBY";
        }
      }
    } catch (err) {
      console.warn("Could not fetch model telemetry:", err);
    }
  }

  async fetchHomeLiveStats() {
    try {
      const resp = await fetch("/api/household/impact");
      const data = await resp.json();
      if (data.status === "success") {
        const m = data.household_metrics || {};

        const elScans = document.getElementById("home-stat-scans");
        const elConfirmed = document.getElementById("home-stat-confirmed");
        const elDiverted = document.getElementById("home-stat-diverted");
        const elOffset = document.getElementById("home-stat-offset");

        if (elScans) elScans.textContent = m.total_scans_performed || 0;
        if (elConfirmed) elConfirmed.textContent = m.total_items_confirmed || 0;
        if (elDiverted) elDiverted.textContent = `${m.diverted_weight_kg || 0} kg`;
        if (elOffset) elOffset.textContent = `${m.avoided_ghg_emissions_kg_co2e || 0} kg CO₂e`;
      }
    } catch (err) {
      console.warn("Could not fetch live homepage stats:", err);
    }
  }

  showToast(message, type = "success") {
    const container = document.getElementById("ecosync-toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `ecosync-toast ${type}`;
    const icon = type === "success" ? "✓" : (type === "warning" ? "⚠️" : "ℹ️");
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(12px)";
      setTimeout(() => toast.remove(), 250);
    }, 3800);
  }

  initTheme() {
    const savedTheme = localStorage.getItem("ecosync_theme") || "dark";
    if (savedTheme === "light") {
      document.body.classList.add("light-theme");
      this.updateThemeIcon(true);
    }

    const btnTheme = document.getElementById("btn-theme-toggle");
    if (btnTheme) {
      btnTheme.addEventListener("click", () => {
        document.body.classList.toggle("light-theme");
        const isLight = document.body.classList.contains("light-theme");
        localStorage.setItem("ecosync_theme", isLight ? "light" : "dark");
        this.updateThemeIcon(isLight);
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast(isLight ? "Clean Light Theme Active" : "Obsidian Cyber Dark Active");
        }
      });
    }
  }

  updateThemeIcon(isLight) {
    const icon = document.getElementById("theme-toggle-icon");
    if (!icon) return;
    if (isLight) {
      icon.innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>`;
    } else {
      icon.innerHTML = `
        <circle cx="12" cy="12" r="5"></circle>
        <line x1="12" y1="1" x2="12" y2="3"></line>
        <line x1="12" y1="21" x2="12" y2="23"></line>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
        <line x1="1" y1="12" x2="3" y2="12"></line>
        <line x1="21" y1="12" x2="23" y2="12"></line>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
      `;
    }
  }

  initWelcomeModal() {
    const modal = document.getElementById("welcome-launch-modal");
    if (!modal) return;

    const slogans = [
      "\"Smart Segregation Starts at the Source.\"",
      "\"Turning Everyday Waste into Circular Value.\"",
      "\"AI-Powered Vision & Real-Time Campus Digital Twin.\"",
      "\"Zero Landfill. 100% Resource Recovery.\"",
      "\"Precision Sorting for a Greener Tomorrow.\""
    ];

    const sloganEl = document.getElementById("welcome-slogan-text");
    const fillEl = document.getElementById("welcome-calib-fill");
    const statusEl = document.getElementById("welcome-calib-status");
    const calibWrap = document.getElementById("welcome-calib-wrap");
    const optionsGrid = document.getElementById("welcome-options-grid");
    const btnSkip = document.getElementById("btn-skip-loading");

    // Rotate 5 slogans smoothly across the 10 seconds (every 2.0 seconds)
    let sloganIdx = 0;
    const sloganTimer = setInterval(() => {
      sloganIdx = (sloganIdx + 1) % slogans.length;
      if (sloganEl) {
        sloganEl.style.opacity = "0";
        setTimeout(() => {
          sloganEl.textContent = slogans[sloganIdx];
          sloganEl.style.opacity = "1";
        }, 220);
      }
    }, 2000);

    // 10-second calibration timer (10,000 milliseconds)
    const TOTAL_MS = 10000;
    const STEP_MS = 100;
    let elapsedMs = 0;

    const finishCalibration = () => {
      clearInterval(progressTimer);
      clearInterval(sloganTimer);
      if (fillEl) fillEl.style.width = "100%";
      if (statusEl) statusEl.textContent = "CALIBRATION COMPLETE // READY FOR OPERATION (100%)";
      setTimeout(() => {
        if (calibWrap) {
          calibWrap.style.transition = "opacity 0.3s ease";
          calibWrap.style.opacity = "0";
          setTimeout(() => {
            calibWrap.style.display = "none";
            if (optionsGrid) {
              optionsGrid.style.display = "grid";
              setTimeout(() => {
                optionsGrid.style.opacity = "1";
              }, 40);
            }
          }, 300);
        }
      }, 400);
    };

    const progressTimer = setInterval(() => {
      elapsedMs += STEP_MS;
      const pct = Math.min(100, Math.floor((elapsedMs / TOTAL_MS) * 100));
      const secLeft = Math.max(0, Math.ceil((TOTAL_MS - elapsedMs) / 1000));

      if (fillEl) fillEl.style.width = `${pct}%`;
      if (statusEl) statusEl.textContent = `CALIBRATING CIRCULAR INTELLIGENCE... ${pct}% (${secLeft}s remaining)`;

      if (elapsedMs >= TOTAL_MS) {
        finishCalibration();
      }
    }, STEP_MS);

    if (btnSkip) {
      btnSkip.addEventListener("click", () => {
        finishCalibration();
      });
    }

    // Mode Option 1: Let's Explore (User mode - clean slate, requires user to add data)
    const btnExplore = document.getElementById("btn-mode-explore");
    if (btnExplore) {
      btnExplore.addEventListener("click", async () => {
        try {
          await fetch("/api/demo/clean-mode", { method: "POST" });
        } catch (e) {
          console.warn("Could not set clean mode:", e);
        }
        this.setDemoState(false);
        modal.style.transition = "opacity 0.4s ease";
        modal.style.opacity = "0";
        setTimeout(() => modal.style.display = "none", 400);
        this.switchView("scanner");
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast("Live User Operation active: Upload or snap items with your camera to add data.");
        }
        if (window.householdImpact) {
          window.householdImpact.fetchImpactMetrics();
          window.householdImpact.fetchHistory();
        }
      });
    }

    // Mode Option 2: View Demo (Built-in demonstration dataset)
    const btnDemo = document.getElementById("btn-mode-demo");
    if (btnDemo) {
      btnDemo.addEventListener("click", async () => {
        try {
          await fetch("/api/demo/reset", { method: "POST" });
        } catch (e) {
          console.warn("Could not reset demo:", e);
        }
        this.setDemoState(true);
        modal.style.transition = "opacity 0.4s ease";
        modal.style.opacity = "0";
        setTimeout(() => modal.style.display = "none", 400);
        this.switchView("home");
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast("Demo Ecosystem active with pre-built campus telemetry and sample streams.");
        }
        if (window.householdImpact) {
          window.householdImpact.fetchImpactMetrics();
          window.householdImpact.fetchHistory();
        }
      });
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.ecosyncApp = new EcoSyncApp();
});
