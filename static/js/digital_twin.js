/**
 * ECOSYNC — Digital Twin Command Centre & Campus Telemetry
 * Matches Reference Images 5, 6, 22.
 */

class DigitalTwin {
  constructor() {
    this.currentBinCode = "BIN-05";
    this.binsData = this.getDefaultBins();
    const saved = localStorage.getItem("ecosync_smart_bins");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          this.binsData = parsed;
        }
      } catch (e) {}
    }
    this.init();
  }

  getDefaultBins() {
    return [
      { code: "BIN-01", name: "Main Library Entrance", location: "Main Library Entrance", stream: "Clean Recyclables", stream_type: "Recyclables", capacity_l: 240, current_fill_pct: 42, battery_pct: 95, last_serviced: "2 hours ago", status: "Operational" },
      { code: "BIN-02", name: "Dining Hall Organics Hub", location: "Dining Hall Exterior", stream: "Organic & Food Compost", stream_type: "Wet Compost", capacity_l: 360, current_fill_pct: 88, battery_pct: 82, last_serviced: "4 hours ago", status: "Warning" },
      { code: "BIN-03", name: "Engineering Quad A", location: "Engineering Quad A", stream: "Dry Recyclables & Paper", stream_type: "Dry Recyclables", capacity_l: 240, current_fill_pct: 35, battery_pct: 98, last_serviced: "1 hour ago", status: "Operational" },
      { code: "BIN-04", name: "Sports Arena Station", location: "Sports Complex", stream: "Beverage Bottles & Cans", stream_type: "Dry Waste", capacity_l: 360, current_fill_pct: 74, battery_pct: 89, last_serviced: "3 hours ago", status: "Operational" },
      { code: "BIN-05", name: "Administration Annex Central", location: "Administration Annex", stream: "General Mixed Trash", stream_type: "General Trash", capacity_l: 400, current_fill_pct: 96, battery_pct: 76, last_serviced: "6 hours ago", status: "Critical Alert" },
      { code: "BIN-06", name: "Science Laboratories Hub", location: "Science Laboratory B", stream: "Hazardous / Batteries & E-Waste", stream_type: "Hazardous / E-Waste", capacity_l: 120, current_fill_pct: 55, battery_pct: 91, last_serviced: "2 hours ago", status: "Operational" },
      { code: "BIN-07", name: "Hostel Block North", location: "Hostel Block North", stream: "Wet Food Scrap Compost", stream_type: "Wet Compost", capacity_l: 240, current_fill_pct: 68, battery_pct: 87, last_serviced: "3 hours ago", status: "Operational" },
      { code: "BIN-08", name: "East Gate Commercial Point", location: "East Gate Plaza", stream: "Dry Recyclables & Packaging", stream_type: "Recyclables", capacity_l: 240, current_fill_pct: 48, battery_pct: 94, last_serviced: "5 hours ago", status: "Operational" }
    ];
  }

  init() {
    this.renderSmartBinsTable();
    this.updateRadarNodes();
    this.selectBin(this.currentBinCode);

    const btnService = document.getElementById("btn-service-bin");
    if (btnService) {
      btnService.onclick = (e) => {
        e.preventDefault();
        this.serviceCurrentBin();
      };
    }

    this.fetchBins();
    this.fetchRoutes();
    this.initScenarioSliders();
  }

  async fetchBins() {
    try {
      const resp = await fetch("/api/bins");
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      if (data.status === "success" && Array.isArray(data.bins) && data.bins.length > 0) {
        // Sync with any local servicing overrides
        const localBins = JSON.parse(localStorage.getItem("ecosync_smart_bins") || "[]");
        const localOverrides = {};
        localBins.forEach(lb => { localOverrides[lb.code] = lb; });

        this.binsData = data.bins.map(b => {
          if (localOverrides[b.code] && localOverrides[b.code].current_fill_pct === 0) {
            return { ...b, ...localOverrides[b.code] };
          }
          return b;
        });

        this.renderSmartBinsTable();
        this.updateRadarNodes();
        this.selectBin(this.currentBinCode);
        return;
      }
      throw new Error("No bin data returned");
    } catch (err) {
      // Offline / GitHub Pages fallback is already active from constructor
      this.renderSmartBinsTable();
      this.updateRadarNodes();
      this.selectBin(this.currentBinCode);
    }
  }

  async fetchRoutes() {
    try {
      const resp = await fetch("/api/routes");
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      if (data.status === "success" && data.routes) {
        this.renderRoutesList(data.routes);
        return;
      }
      throw new Error("No routes returned");
    } catch (err) {
      console.warn("Using local campus route telemetry:", err);
      const dispatched = JSON.parse(localStorage.getItem("ecosync_dispatched_routes") || "{}");
      const fallbackRoutes = [
        { id: "TRK-R01", name: "Zone A Priority Express", status: dispatched["TRK-R01"] || "Dispatched" },
        { id: "TRK-R02", name: "Cafeteria Organics Daily", status: dispatched["TRK-R02"] || "In Transit" },
        { id: "TRK-R03", name: "Academic Blocks Routine", status: dispatched["TRK-R03"] || "Pending" }
      ];
      this.renderRoutesList(fallbackRoutes);
    }
  }

  renderRoutesList(routes) {
    routes.forEach(r => {
      const idKey = r.id.toLowerCase().replace(/[^a-z0-9]/g, '');
      const statusEl = document.getElementById(`route-${idKey}-status`);
      const btnEl = document.getElementById(`btn-dispatch-${idKey}`);
      if (statusEl) {
        statusEl.textContent = `Status: ${r.status}`;
        statusEl.style.color = (r.status === "Dispatched" || r.status === "In Transit") ? "var(--brand-neon)" : "var(--text-secondary)";
        statusEl.style.fontWeight = (r.status === "Dispatched" || r.status === "In Transit") ? "700" : "400";
      }
      if (btnEl) {
        if (r.status === "Dispatched") {
          btnEl.textContent = "✓ Dispatched · En Route (GPS Live)";
          btnEl.style.borderColor = "var(--brand-neon)";
          btnEl.style.color = "var(--brand-neon)";
          btnEl.style.background = "rgba(0, 229, 153, 0.12)";
        } else if (r.status === "In Transit") {
          btnEl.textContent = "✓ In Transit · Active Tracking";
          btnEl.style.borderColor = "var(--brand-neon)";
          btnEl.style.color = "var(--brand-neon)";
          btnEl.style.background = "rgba(0, 229, 153, 0.12)";
        } else {
          btnEl.textContent = "🚛 Dispatch Route Truck";
          btnEl.style.borderColor = "";
          btnEl.style.color = "";
          btnEl.style.background = "";
        }
      }
    });
  }

  updateRadarNodes() {
    this.binsData.forEach(bin => {
      const nodeEl = document.querySelector(`.radar-bin-node[data-bin="${bin.code}"]`);
      if (nodeEl) {
        nodeEl.textContent = `${bin.current_fill_pct}%`;
        nodeEl.className = "radar-bin-node";
        if (bin.current_fill_pct >= 90) {
          nodeEl.classList.add("node-critical");
        } else if (bin.current_fill_pct >= 75) {
          nodeEl.classList.add("node-warning");
        } else {
          nodeEl.classList.add("node-normal");
        }
        if (bin.code === this.currentBinCode) {
          nodeEl.classList.add("selected");
        }
      }
    });
  }

  selectBin(binCode) {
    this.currentBinCode = binCode;
    const bin = this.binsData.find(b => b.code === binCode);
    if (!bin) return;

    // Highlight node on radar map
    document.querySelectorAll(".radar-bin-node").forEach(n => {
      n.classList.toggle("selected", n.getAttribute("data-bin") === binCode);
    });

    // Update inspector panel fields
    const elCode = document.getElementById("inspector-bin-code");
    const elName = document.getElementById("inspector-name");
    const elLocation = document.getElementById("inspector-location");
    const elStream = document.getElementById("inspector-stream");
    const elBattery = document.getElementById("inspector-battery");
    const elFillNum = document.getElementById("inspector-fill-num");
    const elFillBar = document.getElementById("inspector-fill-bar");
    const elBadge = document.getElementById("inspector-status-badge");
    const btnService = document.getElementById("btn-service-bin");

    if (elCode) elCode.textContent = bin.code;
    if (elName) elName.textContent = bin.name || bin.location || "Smart Waste Station";
    if (elLocation) elLocation.textContent = bin.location;
    if (elStream) elStream.textContent = bin.stream || bin.stream_type || "General Waste";
    if (elBattery) elBattery.textContent = `${bin.battery_pct}%`;
    if (elFillNum) {
      elFillNum.textContent = `${bin.current_fill_pct}%`;
      elFillNum.style.color = bin.current_fill_pct >= 90 ? "#ef4444" : (bin.current_fill_pct >= 75 ? "#f59e0b" : "#10b981");
    }
    if (elFillBar) {
      elFillBar.style.width = `${bin.current_fill_pct}%`;
      elFillBar.style.backgroundColor = bin.current_fill_pct >= 90 ? "#ef4444" : (bin.current_fill_pct >= 75 ? "#f59e0b" : "#10b981");
    }
    if (elBadge) {
      elBadge.className = "tax-pill-badge";
      if (bin.current_fill_pct >= 90 || bin.status.toLowerCase().includes("critical")) {
        elBadge.classList.add("tax-pill-red");
        elBadge.textContent = "Critical Alert (Empty Needed)";
      } else if (bin.current_fill_pct >= 75 || bin.status.toLowerCase().includes("warning")) {
        elBadge.classList.add("tax-pill-orange");
        elBadge.textContent = "High Capacity Warning";
      } else {
        elBadge.classList.add("tax-pill-green");
        elBadge.textContent = "Operational (Normal)";
      }
    }
    if (btnService) {
      if (bin.current_fill_pct === 0) {
        btnService.textContent = `✓ ${bin.code} EMPTIED (0% - OPERATIONAL)`;
        btnService.style.background = "#059669";
        btnService.style.color = "#ffffff";
      } else {
        btnService.textContent = `SERVICE / EMPTY ${bin.code} (${bin.current_fill_pct}%)`;
        btnService.style.background = "";
        btnService.style.color = "";
      }
    }
  }

  async serviceCurrentBin() {
    const code = this.currentBinCode || "BIN-05";
    if (!this.binsData || !this.binsData.length) {
      this.binsData = this.getDefaultBins();
    }
    let bin = this.binsData.find(b => b.code === code);
    if (!bin) {
      bin = this.binsData.find(b => b.code === "BIN-05") || this.binsData[0];
      if (bin) this.currentBinCode = bin.code;
    }

    const prevFill = bin ? bin.current_fill_pct : 96;

    // 1. Immediately update local state & persistence synchronously
    if (bin) {
      bin.current_fill_pct = 0;
      bin.status = "Operational";
      bin.last_serviced = "Just now";
      localStorage.setItem("ecosync_smart_bins", JSON.stringify(this.binsData));
    }

    // 2. Direct instant DOM updates
    const btn = document.getElementById("btn-service-bin");
    if (btn) {
      btn.disabled = false;
      btn.textContent = `✓ ${code} EMPTIED (0% - OPERATIONAL)`;
      btn.style.background = "#059669";
      btn.style.color = "#ffffff";
      btn.style.boxShadow = "0 0 18px rgba(16, 185, 129, 0.4)";
    }

    const elFillNum = document.getElementById("inspector-fill-num");
    const elFillBar = document.getElementById("inspector-fill-bar");
    const elBadge = document.getElementById("inspector-status-badge");
    if (elFillNum) {
      elFillNum.textContent = "0%";
      elFillNum.style.color = "#10b981";
    }
    if (elFillBar) {
      elFillBar.style.width = "0%";
      elFillBar.style.backgroundColor = "#10b981";
    }
    if (elBadge) {
      elBadge.className = "tax-pill-badge tax-pill-green";
      elBadge.textContent = "Operational (Normal)";
    }

    this.renderSmartBinsTable();
    this.updateRadarNodes();

    // 3. User feedback toast
    if (window.showEcoSyncToast) {
      window.showEcoSyncToast(`✓ Station ${code} (${bin ? bin.name : 'Smart Bin'}) emptied! Fill level: 0%. Collection alert cleared.`);
    }

    // 4. Non-blocking background API notification
    try {
      fetch(`/api/bins/${code}/service`, { method: "POST" }).catch(() => {});
    } catch (e) {}
  }

  async dispatchRoute(routeId) {
    const idKey = routeId.toLowerCase().replace(/[^a-z0-9]/g, '');
    const btn = document.getElementById(`btn-dispatch-${idKey}`);
    const statusEl = document.getElementById(`route-${idKey}-status`);

    if (btn) {
      btn.disabled = true;
      btn.textContent = "Dispatching Route...";
    }

    try {
      const resp = await fetch(`/api/routes/${routeId}/dispatch`, { method: "POST" });
      const data = await resp.json();
      if (data.status === "success") {
        await this.fetchRoutes();
      } else {
        throw new Error(data.message || "Dispatch error");
      }
    } catch (err) {
      console.warn("Client-side route dispatch execution:", err);
      const dispatched = JSON.parse(localStorage.getItem("ecosync_dispatched_routes") || "{}");
      dispatched[routeId] = "Dispatched";
      localStorage.setItem("ecosync_dispatched_routes", JSON.stringify(dispatched));
    }

    if (statusEl) {
      statusEl.textContent = "Status: Dispatched (En Route)";
      statusEl.style.color = "var(--brand-neon)";
      statusEl.style.fontWeight = "700";
    }
    if (btn) {
      btn.disabled = false;
      btn.textContent = "✓ Dispatched · En Route (GPS Live)";
      btn.style.borderColor = "var(--brand-neon)";
      btn.style.color = "var(--brand-neon)";
      btn.style.background = "rgba(0, 229, 153, 0.12)";
    }

    if (window.showEcoSyncToast) {
      window.showEcoSyncToast(`🚛 Collection Vehicle ${routeId} dispatched! Fleet route active with GPS tracking.`);
    }
  }

  renderSmartBinsTable() {
    const tbody = document.getElementById("smart-bins-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    this.binsData.forEach(bin => {
      const tr = document.createElement("tr");
      const isCrit = bin.status.toLowerCase().includes("critical");
      const isNear = bin.status.toLowerCase().includes("near");
      const badgeClass = isCrit ? "tax-pill-red" : (isNear ? "tax-pill-orange" : "tax-pill-green");
      const barColor = isCrit ? "#ef4444" : (isNear ? "#f59e0b" : "#10b981");

      tr.innerHTML = `
        <td style="font-family:var(--font-mono); font-weight:700; color:var(--brand-neon);">${bin.code}</td>
        <td>
          <div style="font-weight:600; color:#fff;">${bin.name}</div>
          <div style="font-size:12px; color:var(--text-muted);">${bin.location}</div>
        </td>
        <td>${bin.stream}</td>
        <td style="font-family:var(--font-mono);">${bin.capacity_l} L</td>
        <td style="min-width:140px;">
          <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
            <span>${bin.current_fill_pct}%</span>
          </div>
          <div class="progress-track" style="margin:0;">
            <div class="progress-fill" style="width:${bin.current_fill_pct}%; background-color:${barColor};"></div>
          </div>
        </td>
        <td style="font-family:var(--font-mono);">${bin.battery_pct}%</td>
        <td><span class="tax-pill-badge ${badgeClass}">${bin.status}</span></td>
        <td style="font-size:12px; color:var(--text-muted);">${bin.last_serviced}</td>
        <td>
          <button class="btn-demo-action" onclick="window.ecosyncTwin.selectBin('${bin.code}'); window.ecosyncTwin.serviceCurrentBin();">
            Empty Bin
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  initScenarioSliders() {
    const slSeg = document.getElementById("sim-seg-rate");
    const slVol = document.getElementById("sim-vol-rate");
    const slCap = document.getElementById("sim-cap-rate");

    const valSeg = document.getElementById("sim-seg-val");
    const valVol = document.getElementById("sim-vol-val");
    const valCap = document.getElementById("sim-cap-val");

    const txtOutput = document.getElementById("sim-comparison-text");

    const runSim = async () => {
      const seg = parseFloat(slSeg?.value || 65);
      const vol = parseFloat(slVol?.value || 200);
      const cap = parseFloat(slCap?.value || 220);

      if (valSeg) valSeg.textContent = `${seg}%`;
      if (valVol) valVol.textContent = `${vol} TPD`;
      if (valCap) valCap.textContent = `${cap} TPD`;

      try {
        const resp = await fetch("/api/simulation/scenario", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            segregation_rate_pct: seg,
            daily_volume_tons: vol,
            processing_capacity_tpd: cap
          })
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const res = await resp.json();
        if (res.status === "success" && txtOutput) {
          const comp = res.comparison || {};
          txtOutput.innerHTML = `
            <strong>Scenario vs. Baseline (35% Source Segregation):</strong><br>
            • Landfill Diversion Rate Gain: <span style="color:var(--brand-neon); font-weight:700;">+${comp.diversion_rate_gain_pct || 0}%</span><br>
            • Daily Waste Kept from Landfills: <span style="color:var(--brand-neon); font-weight:700;">+${comp.landfill_reduction_tons_per_day || 0} Tons/Day</span><br>
            • Avoided Methane & GHG Emissions: <span style="color:#34d399; font-weight:700;">-${comp.avoided_ghg_emissions_kg_co2e_per_day || 0} kg CO₂e/Day</span><br>
            • Contamination Load Avoided: <span style="color:#60a5fa; font-weight:700;">-${comp.contamination_reduction_tons_per_day || 0} Tons/Day</span>
          `;
          return;
        }
        throw new Error("Simulation endpoint error");
      } catch (err) {
        // Deterministic local simulation math
        const baseRec = (vol * 0.35 * 0.70);
        const scenRec = (vol * (seg / 100.0) * 0.85);
        const gainPct = Math.max(0, Math.round(((scenRec - baseRec) / vol) * 100));
        const tonsDiverted = Math.max(0, (scenRec - baseRec)).toFixed(1);
        const ghgKg = Math.round(parseFloat(tonsDiverted) * 850);
        const contamTons = Math.max(0, (vol * (1 - seg / 100.0) * 0.12)).toFixed(1);

        if (txtOutput) {
          txtOutput.innerHTML = `
            <strong>Scenario vs. Baseline (35% Source Segregation):</strong><br>
            • Landfill Diversion Rate Gain: <span style="color:var(--brand-neon); font-weight:700;">+${gainPct}%</span><br>
            • Daily Waste Kept from Landfills: <span style="color:var(--brand-neon); font-weight:700;">+${tonsDiverted} Tons/Day</span><br>
            • Avoided Methane & GHG Emissions: <span style="color:#34d399; font-weight:700;">-${ghgKg} kg CO₂e/Day</span><br>
            • Contamination Load Avoided: <span style="color:#60a5fa; font-weight:700;">-${contamTons} Tons/Day</span>
          `;
        }
      }
    };

    [slSeg, slVol, slCap].forEach(sl => {
      if (sl) sl.addEventListener("input", runSim);
    });

    runSim();
  }
}

window.digitalTwin = new DigitalTwin();
window.ecosyncTwin = window.digitalTwin;
window.serviceCurrentBin = () => window.digitalTwin?.serviceCurrentBin();
