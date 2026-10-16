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
    if (typeof WasteScanner !== "undefined") window.wasteScanner = new WasteScanner();
    if (typeof WasteGuide !== "undefined") window.wasteGuide = new WasteGuide();
    if (typeof DigitalTwin !== "undefined") window.digitalTwin = new DigitalTwin();
    if (typeof HouseholdImpact !== "undefined") window.householdImpact = new HouseholdImpact();
    if (typeof AIAdvisor !== "undefined") window.aiAdvisor = new AIAdvisor();

    // 3. Navigation routing
    this.isDemoMode = true;
    this.initNavigation();
    this.initHomeActions();
    this.initQuickBinFinder();
    this.initDemoModeControls();

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
    const openWalkthrough = () => {
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
      setTimeout(() => {
        window.digitalTwin.resize();
        window.digitalTwin.fetchTopology();
      }, 100);
    } else if (viewId === "guide" && window.wasteGuide) {
      window.wasteGuide.fetchItems();
    } else if (viewId === "impact" && window.householdImpact) {
      window.householdImpact.fetchImpactMetrics();
      window.householdImpact.fetchHistory();
    } else if (viewId === "advisor" && window.aiAdvisor) {
      const input = document.getElementById("advisor-query-input");
      if (input) setTimeout(() => input.focus(), 150);
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
}

document.addEventListener("DOMContentLoaded", () => {
  window.ecosyncApp = new EcoSyncApp();
});
