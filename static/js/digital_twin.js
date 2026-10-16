/**
 * ECOSYNC — Circular Waste Ecosystem Digital Twin
 * Interactive visual model of the household-to-recycler journey:
 * 1. Household Kitchen Source -> 2. Neighborhood Route -> 3. MRF Optical Sorting -> 4. Secondary Refiners
 * Animated flow particles, interactive node inspector, state machine transitions, and scenario simulator.
 */

class DigitalTwin {
  constructor() {
    this.canvas = document.getElementById("twin-topology-canvas");
    this.ctx = this.canvas ? this.canvas.getContext("2d") : null;
    this.inspectorCard = document.getElementById("twin-node-inspector");

    this.btnStepSim = document.getElementById("btn-sim-step");
    this.btnResetSim = document.getElementById("btn-sim-reset");
    this.btnAutoSim = document.getElementById("btn-sim-auto");

    // Modal elements
    this.batchModal = document.getElementById("batch-detail-modal");
    this.batchModalBody = document.getElementById("batch-detail-modal-body");

    // State
    this.topologyData = null;
    this.selectedNode = null;
    this.isAutoRunning = false;
    this.autoInterval = null;

    // Animated particles
    this.particles = [];
    this.tick = 0;

    // Node layout coordinates (normalized 0.0 to 1.0)
    this.nodePositions = {
      // 1. Starting household node
      "HOME": { x: 0.08, y: 0.52, type: "home", label: "Household Kitchen", icon: "🏡" },

      // 2. Collection points (Neighborhood hubs)
      "CP-ALPHA": { x: 0.28, y: 0.22, type: "cp", label: "Harbor Route (Alpha)", icon: "🚛" },
      "CP-BETA": { x: 0.28, y: 0.42, type: "cp", label: "Logistics Hub (Beta)", icon: "🚛" },
      "CP-GAMMA": { x: 0.28, y: 0.62, type: "cp", label: "Downtown Metro (Gamma)", icon: "🚛" },
      "CP-DELTA": { x: 0.28, y: 0.82, type: "cp", label: "Eastside Suburbs (Delta)", icon: "🚛" },

      // 3. Central MRF hub
      "MRF-01": { x: 0.56, y: 0.52, type: "facility", label: "MRF-01 Optical Recovery", icon: "⚙️" },

      // 4. Specialized Processing Facilities
      "PRP-02": { x: 0.86, y: 0.22, type: "facility", label: "PRP-02 Polymer Flake", icon: "🔄" },
      "FPU-03": { x: 0.86, y: 0.42, type: "facility", label: "FPU-03 Fiber/Pulping", icon: "🔄" },
      "MSR-04": { x: 0.86, y: 0.62, type: "facility", label: "MSR-04 Alloy Smelting", icon: "🔄" },
      "GBC-05": { x: 0.86, y: 0.82, type: "facility", label: "GBC-05 Glass Cullet", icon: "🔄" }
    };

    this.init();
  }

  init() {
    if (!this.canvas) return;

    this.resize();
    window.addEventListener("resize", () => this.resize());

    this.fetchTopology();

    // Canvas click to select node
    this.canvas.addEventListener("click", (e) => this.onCanvasClick(e));

    // Simulation controls
    if (this.btnStepSim) {
      this.btnStepSim.addEventListener("click", () => this.stepSimulation());
    }
    if (this.btnResetSim) {
      this.btnResetSim.addEventListener("click", () => this.resetSimulation());
    }
    if (this.btnAutoSim) {
      this.btnAutoSim.addEventListener("click", () => this.toggleAutoSimulation());
    }

    // Modal close
    document.querySelectorAll(".modal-close-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (this.batchModal) this.batchModal.style.display = "none";
      });
    });

    // Start render loop
    this.render = this.render.bind(this);
    requestAnimationFrame(this.render);

    // Initialize interactive scenario simulator
    this.initScenarioSimulator();
  }

  initScenarioSimulator() {
    const sliderVol = document.getElementById("sim-slider-volume");
    const sliderSeg = document.getElementById("sim-slider-segregation");
    const sliderColl = document.getElementById("sim-slider-collection");
    const sliderProc = document.getElementById("sim-slider-processing");

    if (!sliderVol) return;

    const updateAndRun = () => {
      const v = sliderVol ? sliderVol.value : 200;
      const s = sliderSeg ? sliderSeg.value : 65;
      const c = sliderColl ? sliderColl.value : 250;
      const p = sliderProc ? sliderProc.value : 220;

      const txtV = document.getElementById("sim-val-volume");
      const txtS = document.getElementById("sim-val-segregation");
      const txtC = document.getElementById("sim-val-collection");
      const txtP = document.getElementById("sim-val-processing");

      if (txtV) txtV.textContent = `${v} TPD`;
      if (txtS) txtS.textContent = `${s}%`;
      if (txtC) txtC.textContent = `${c} TPD`;
      if (txtP) txtP.textContent = `${p} TPD`;

      this.runScenarioProjection(v, s, c, p);
    };

    [sliderVol, sliderSeg, sliderColl, sliderProc].forEach((slider) => {
      if (slider) {
        slider.addEventListener("input", updateAndRun);
      }
    });

    // Preset buttons
    const btnBase = document.getElementById("preset-baseline");
    const btnHigh = document.getElementById("preset-high-segregation");
    const btnStress = document.getElementById("preset-stress");

    if (btnBase) {
      btnBase.addEventListener("click", () => {
        if (sliderVol) sliderVol.value = 220;
        if (sliderSeg) sliderSeg.value = 35;
        if (sliderColl) sliderColl.value = 250;
        if (sliderProc) sliderProc.value = 200;
        updateAndRun();
      });
    }

    if (btnHigh) {
      btnHigh.addEventListener("click", () => {
        if (sliderVol) sliderVol.value = 200;
        if (sliderSeg) sliderSeg.value = 85;
        if (sliderColl) sliderColl.value = 260;
        if (sliderProc) sliderProc.value = 220;
        updateAndRun();
      });
    }

    if (btnStress) {
      btnStress.addEventListener("click", () => {
        if (sliderVol) sliderVol.value = 380;
        if (sliderSeg) sliderSeg.value = 45;
        if (sliderColl) sliderColl.value = 220;
        if (sliderProc) sliderProc.value = 180;
        updateAndRun();
      });
    }

    // Initial projection run
    updateAndRun();
  }

  async runScenarioProjection(volume, segregation, collection, processing) {
    try {
      const resp = await fetch("/api/simulation/scenario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          daily_volume_tons: parseFloat(volume),
          segregation_rate_pct: parseFloat(segregation),
          collection_capacity_tpd: parseFloat(collection),
          processing_capacity_tpd: parseFloat(processing)
        })
      });

      const data = await resp.json();
      if (data.status === "success") {
        this.renderScenarioResults(data);
      }
    } catch (err) {
      console.error("Scenario projection error:", err);
    }
  }

  renderScenarioResults(projection) {
    const m = projection.metrics || {};
    const divEl = document.getElementById("sim-res-diversion");
    const utilEl = document.getElementById("sim-res-overflow");
    const co2El = document.getElementById("sim-res-co2");
    const recEl = document.getElementById("sim-res-recommendation");

    if (divEl) divEl.textContent = `${m.diversion_rate_pct}%`;
    if (utilEl) {
      utilEl.textContent = `${m.collection_utilization_pct}%`;
      utilEl.style.color = m.collection_utilization_pct > 100 ? "#ef4444" : "#10b981";
    }
    if (co2El) co2El.textContent = `${m.avoided_co2e_metric_tons} MT`;
    if (recEl) recEl.textContent = projection.recommendation || "";

    // Render Before vs After Comparison Table
    if (projection.comparison) {
      const c = projection.comparison;
      const b = c.baseline || {};
      const s = c.scenario || {};
      const d = c.deltas || {};

      const elBaseDiv = document.getElementById("comp-base-diversion");
      const elScenDiv = document.getElementById("comp-scen-diversion");
      const elDeltaDiv = document.getElementById("comp-delta-diversion");

      const elBaseLand = document.getElementById("comp-base-landfill");
      const elScenLand = document.getElementById("comp-scen-landfill");
      const elDeltaLand = document.getElementById("comp-delta-landfill");

      const elBaseCo2 = document.getElementById("comp-base-co2");
      const elScenCo2 = document.getElementById("comp-scen-co2");
      const elDeltaCo2 = document.getElementById("comp-delta-co2");

      const elBaseCont = document.getElementById("comp-base-contam");
      const elScenCont = document.getElementById("comp-scen-contam");
      const elDeltaCont = document.getElementById("comp-delta-contam");

      const elSum = document.getElementById("comp-summary-text");

      if (elBaseDiv) elBaseDiv.textContent = `${b.diversion_rate_pct}%`;
      if (elScenDiv) elScenDiv.textContent = `${s.diversion_rate_pct}%`;
      if (elDeltaDiv) {
        const sign = d.diversion_rate_diff_pct >= 0 ? "+" : "";
        elDeltaDiv.textContent = `${sign}${d.diversion_rate_diff_pct}%`;
        elDeltaDiv.className = `delta-cell ${d.diversion_rate_diff_pct >= 0 ? 'delta-positive' : 'delta-reduction'}`;
      }

      if (elBaseLand) elBaseLand.textContent = `${b.total_landfilled_tons} TPD`;
      if (elScenLand) elScenLand.textContent = `${s.total_landfilled_tons} TPD`;
      if (elDeltaLand) {
        const sign = d.landfill_avoided_diff_tons >= 0 ? "-" : "+";
        elDeltaLand.textContent = `${sign}${Math.abs(d.landfill_avoided_diff_tons)} TPD`;
        elDeltaLand.className = `delta-cell ${d.landfill_avoided_diff_tons >= 0 ? 'delta-positive' : 'delta-reduction'}`;
      }

      if (elBaseCo2) elBaseCo2.textContent = `${b.avoided_co2e_metric_tons} MT`;
      if (elScenCo2) elScenCo2.textContent = `${s.avoided_co2e_metric_tons} MT`;
      if (elDeltaCo2) {
        const sign = d.co2e_offset_diff_mt >= 0 ? "+" : "";
        elDeltaCo2.textContent = `${sign}${d.co2e_offset_diff_mt} MT/d`;
        elDeltaCo2.className = `delta-cell ${d.co2e_offset_diff_mt >= 0 ? 'delta-positive' : 'delta-reduction'}`;
      }

      if (elBaseCont) elBaseCont.textContent = `${b.contamination_loss_tons} TPD`;
      if (elScenCont) elScenCont.textContent = `${s.contamination_loss_tons} TPD`;
      if (elDeltaCont) {
        const sign = d.contamination_saved_diff_tons >= 0 ? "-" : "+";
        elDeltaCont.textContent = `${sign}${Math.abs(d.contamination_saved_diff_tons)} TPD`;
        elDeltaCont.className = `delta-cell ${d.contamination_saved_diff_tons >= 0 ? 'delta-positive' : 'delta-reduction'}`;
      }

      if (elSum && d.improvement_summary) {
        elSum.textContent = d.improvement_summary;
      }
    }
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.width = rect.width;
    this.height = rect.height;
  }

  async fetchTopology() {
    try {
      const resp = await fetch("/api/digital-twin");
      const data = await resp.json();
      if (data.status === "success") {
        this.topologyData = data;
        this.updateDefaultInspector();
      }
    } catch (err) {
      console.error("Failed to load digital twin topology:", err);
    }
  }

  updateDefaultInspector() {
    if (!this.inspectorCard || !this.topologyData) return;
    const fac = this.topologyData.topology.facilities[0];
    this.inspectFacility(fac);
  }

  inspectFacility(fac) {
    if (!this.inspectorCard || !fac) return;
    const loadPct = Math.round((fac.current_load_tpd / fac.capacity_tpd) * 100);

    this.inspectorCard.innerHTML = `
      <div class="inspector-title">${fac.name}</div>
      <div style="font-family: var(--font-mono); font-size: 11px; color: var(--brand-accent);">${fac.facility_type} // ${fac.id}</div>
      <div class="inspector-meta-grid">
        <div class="inspector-meta-item">
          <span>OPERATIONAL STATUS</span>
          <strong style="color: #10b981; text-transform: uppercase;">${fac.status}</strong>
        </div>
        <div class="inspector-meta-item">
          <span>CURRENT LOAD</span>
          <strong>${fac.current_load_tpd} / ${fac.capacity_tpd} TPD (${loadPct}%)</strong>
        </div>
        <div class="inspector-meta-item">
          <span>SORTING EFFICIENCY</span>
          <strong>${Math.round(fac.efficiency_rate * 100)}% OPTICAL YIELD</strong>
        </div>
        <div class="inspector-meta-item">
          <span>SUPPORTED STREAMS</span>
          <strong>${fac.supported_materials}</strong>
        </div>
      </div>
      <div style="margin-top: 12px; font-size: 12px; color: var(--text-secondary); line-height: 1.45;">
        <strong>Household Impact:</strong> Proper rinsing and removing non-compatible caps keeps optical sorting conveyors running at peak 92% throughput without jams.
      </div>
    `;
  }

  inspectCollectionPoint(cp) {
    if (!this.inspectorCard || !cp) return;
    this.inspectorCard.innerHTML = `
      <div class="inspector-title">${cp.name}</div>
      <div style="font-family: var(--font-mono); font-size: 11px; color: #f59e0b;">NEIGHBORHOOD DEPOT // ${cp.id}</div>
      <div class="inspector-meta-grid">
        <div class="inspector-meta-item">
          <span>BIN FILL LEVEL</span>
          <strong style="color: ${cp.fill_level_pct >= 75 ? '#ef4444' : '#10b981'};">${cp.fill_level_pct}%</strong>
        </div>
        <div class="inspector-meta-item">
          <span>ASSIGNED MRF HUB</span>
          <strong>${cp.assigned_facility_id}</strong>
        </div>
        <div class="inspector-meta-item">
          <span>ZONE</span>
          <strong>${cp.zone}</strong>
        </div>
        <div class="inspector-meta-item">
          <span>LAST PICKUP</span>
          <strong>${cp.last_pickup_at ? cp.last_pickup_at.split(' ')[0] : 'Today'}</strong>
        </div>
      </div>
      <div style="margin-top: 12px; font-size: 12px; color: var(--text-secondary); line-height: 1.45;">
        <strong>Household Habit:</strong> Flattening delivery boxes and crushing cans saves up to 70% of collection truck volume, preventing neighborhood bin overflows.
      </div>
    `;
  }

  inspectHousehold() {
    if (!this.inspectorCard) return;
    this.inspectorCard.innerHTML = `
      <div class="inspector-title">Your Household Kitchen</div>
      <div style="font-family: var(--font-mono); font-size: 11px; color: #10b981;">SOURCE SEGREGATION // START OF CIRCULARITY</div>
      <div class="inspector-meta-grid">
        <div class="inspector-meta-item">
          <span>ROLE</span>
          <strong style="color: #10b981;">Origin Source</strong>
        </div>
        <div class="inspector-meta-item">
          <span>PRIMARY STREAMS</span>
          <strong>Recyclables, Organics, Trash</strong>
        </div>
        <div class="inspector-meta-item">
          <span>KEY PREPARATION</span>
          <strong>5-Second Water Rinse</strong>
        </div>
        <div class="inspector-meta-item">
          <span>NEXT STEP</span>
          <strong>Neighborhood Depot</strong>
        </div>
      </div>
      <div style="margin-top: 12px; font-size: 12px; color: var(--text-secondary); line-height: 1.45;">
        <strong>Everyday Action:</strong> Clean, dry separation at the kitchen counter eliminates 95% of cross-contamination in paper and polymer streams downstream!
      </div>
    `;
  }

  async stepSimulation() {
    try {
      const resp = await fetch("/api/simulation/step", { method: "POST" });
      const data = await resp.json();
      if (data.status === "success") {
        this.spawnBatchParticles();
        this.fetchTopology();
        if (window.showEcoSyncToast) window.showEcoSyncToast("Simulation stepped: Materials advanced through sorting network.");
      }
    } catch (err) {
      console.error("Simulation step error:", err);
    }
  }

  async resetSimulation() {
    try {
      const resp = await fetch("/api/simulation/reset", { method: "POST" });
      const data = await resp.json();
      if (data.status === "reset_complete") {
        this.fetchTopology();
        if (window.showEcoSyncToast) window.showEcoSyncToast("Simulation reset to baseline operational state.");
      }
    } catch (err) {
      console.error("Simulation reset error:", err);
    }
  }

  toggleAutoSimulation() {
    this.isAutoRunning = !this.isAutoRunning;
    if (this.btnAutoSim) {
      this.btnAutoSim.textContent = this.isAutoRunning ? "Pause Auto Sim" : "Auto-Run";
      this.btnAutoSim.style.borderColor = this.isAutoRunning ? "#10b981" : "#cbd5e1";
    }
    if (this.isAutoRunning) {
      this.autoInterval = setInterval(() => this.stepSimulation(), 4000);
      if (window.showEcoSyncToast) window.showEcoSyncToast("Auto-simulation active: Generating continuous waste flows.");
    } else {
      clearInterval(this.autoInterval);
      this.autoInterval = null;
    }
  }

  spawnBatchParticles() {
    const routes = [
      { start: "HOME", end: "CP-ALPHA", color: "#38bdf8" },
      { start: "HOME", end: "CP-BETA", color: "#4ade80" },
      { start: "HOME", end: "CP-GAMMA", color: "#fbbf24" },
      { start: "HOME", end: "CP-DELTA", color: "#f472b6" },
      { start: "CP-ALPHA", end: "MRF-01", color: "#38bdf8" },
      { start: "CP-BETA", end: "MRF-01", color: "#4ade80" },
      { start: "CP-GAMMA", end: "MRF-01", color: "#fbbf24" },
      { start: "CP-DELTA", end: "MRF-01", color: "#f472b6" },
      { start: "MRF-01", end: "PRP-02", color: "#38bdf8" },
      { start: "MRF-01", end: "FPU-03", color: "#fcd34d" },
      { start: "MRF-01", end: "MSR-04", color: "#fb923c" },
      { start: "MRF-01", end: "GBC-05", color: "#60a5fa" }
    ];

    routes.forEach((r) => {
      const p1 = this.nodePositions[r.start];
      const p2 = this.nodePositions[r.end];
      if (p1 && p2) {
        this.particles.push({
          x: p1.x * this.width,
          y: p1.y * this.height,
          targetX: p2.x * this.width,
          targetY: p2.y * this.height,
          progress: 0,
          speed: 0.014 + Math.random() * 0.012,
          color: r.color
        });
      }
    });
  }

  onCanvasClick(e) {
    if (!this.canvas) return;
    const rect = this.canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    Object.entries(this.nodePositions).forEach(([id, pos]) => {
      const nx = pos.x * this.width;
      const ny = pos.y * this.height;
      const dist = Math.hypot(clickX - nx, clickY - ny);

      if (dist <= 28) {
        this.selectedNode = id;
        if (id === "HOME") {
          this.inspectHousehold();
        } else if (pos.type === "facility" && this.topologyData) {
          const fac = this.topologyData.topology.facilities.find((f) => f.id === id);
          if (fac) this.inspectFacility(fac);
        } else if (pos.type === "cp" && this.topologyData) {
          const cp = this.topologyData.topology.collection_points.find((c) => c.id === id);
          if (cp) this.inspectCollectionPoint(cp);
        }
      }
    });
  }

  render() {
    if (!this.ctx || !this.canvas) return;

    this.tick++;
    this.ctx.clearRect(0, 0, this.width, this.height);

    // Subtle dark gradient background
    const bgGrad = this.ctx.createLinearGradient(0, 0, this.width, this.height);
    bgGrad.addColorStop(0, "#0b1320");
    bgGrad.addColorStop(1, "#111c30");
    this.ctx.fillStyle = bgGrad;
    this.ctx.fillRect(0, 0, this.width, this.height);

    // 1. Draw Flow Conduits (Links)
    // Connecting HOME to CPs
    ["CP-ALPHA", "CP-BETA", "CP-GAMMA", "CP-DELTA"].forEach((cpId) => {
      const hPos = this.nodePositions["HOME"];
      const cpPos = this.nodePositions[cpId];
      if (hPos && cpPos) {
        this.ctx.beginPath();
        this.ctx.moveTo(hPos.x * this.width, hPos.y * this.height);
        this.ctx.lineTo(cpPos.x * this.width, cpPos.y * this.height);
        this.ctx.strokeStyle = "rgba(56, 189, 248, 0.14)";
        this.ctx.lineWidth = 1.5;
        this.ctx.setLineDash([4, 4]);
        this.ctx.stroke();
        this.ctx.setLineDash([]);
      }
    });

    // Connecting CPs to MRF and MRF to refiners
    const links = (this.topologyData && this.topologyData.topology.flow_links) || [];
    links.forEach((link) => {
      const p1 = this.nodePositions[link.source];
      const p2 = this.nodePositions[link.target];
      if (p1 && p2) {
        const x1 = p1.x * this.width;
        const y1 = p1.y * this.height;
        const x2 = p2.x * this.width;
        const y2 = p2.y * this.height;

        this.ctx.beginPath();
        this.ctx.moveTo(x1, y1);
        const midX = (x1 + x2) / 2;
        const midY = (y1 + y2) / 2;
        this.ctx.quadraticCurveTo(midX, midY, x2, y2);
        this.ctx.strokeStyle = "rgba(148, 163, 184, 0.22)";
        this.ctx.lineWidth = 1.8;
        this.ctx.stroke();
      }
    });

    // 2. Ambient background particles (continuous gentle flow)
    if (this.tick % 45 === 0) {
      this.spawnBatchParticles();
    }

    // 3. Update and draw flow particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.progress += p.speed;

      const curX = p.x + (p.targetX - p.x) * p.progress;
      const curY = p.y + (p.targetY - p.y) * p.progress;

      this.ctx.beginPath();
      this.ctx.arc(curX, curY, 3.5, 0, Math.PI * 2);
      this.ctx.fillStyle = p.color;
      this.ctx.shadowColor = p.color;
      this.ctx.shadowBlur = 6;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;

      if (p.progress >= 1.0) {
        this.particles.splice(i, 1);
      }
    }

    // 4. Draw Nodes
    Object.entries(this.nodePositions).forEach(([id, pos]) => {
      const nx = pos.x * this.width;
      const ny = pos.y * this.height;
      const isFacility = pos.type === "facility";
      const isHome = pos.type === "home";
      const isSelected = this.selectedNode === id;

      this.ctx.save();

      // Outer halo
      this.ctx.beginPath();
      const nodeR = isHome ? 22 : (isFacility ? 24 : 18);
      this.ctx.arc(nx, ny, nodeR, 0, Math.PI * 2);

      let strokeColor = "rgba(148, 163, 184, 0.6)";
      let fillColor = "#1e293b";

      if (isHome) {
        strokeColor = "#10b981";
        fillColor = "#064e3b";
      } else if (isFacility) {
        strokeColor = "#3b82f6";
        fillColor = "#1e3a8a";
      } else {
        strokeColor = "#f59e0b";
        fillColor = "#78350f";
      }

      if (isSelected) {
        strokeColor = "#ffffff";
        this.ctx.lineWidth = 3;
      } else {
        this.ctx.lineWidth = 1.8;
      }

      this.ctx.fillStyle = fillColor;
      this.ctx.fill();
      this.ctx.strokeStyle = strokeColor;
      this.ctx.stroke();

      // Icon
      this.ctx.font = isHome ? "16px sans-serif" : (isFacility ? "15px sans-serif" : "13px sans-serif");
      this.ctx.textAlign = "center";
      this.ctx.textBaseline = "middle";
      this.ctx.fillText(pos.icon || "•", nx, ny);

      // Node ID Label
      this.ctx.font = "bold 11px ui-monospace, SF Mono, monospace";
      this.ctx.fillStyle = "#ffffff";
      this.ctx.fillText(id, nx, ny + nodeR + 13);

      // Node Descriptive Label
      this.ctx.font = "10px system-ui, sans-serif";
      this.ctx.fillStyle = "#94a3b8";
      this.ctx.fillText(pos.label, nx, ny + nodeR + 25);

      this.ctx.restore();
    });

    requestAnimationFrame(this.render);
  }
}

window.DigitalTwin = DigitalTwin;
