/**
 * ECOSYNC — Digital Twin Command Centre & Campus Telemetry
 * Matches Reference Images 5, 6, 22.
 */

class DigitalTwin {
  constructor() {
    this.currentBinCode = "BIN-05";
    this.binsData = [];
    this.init();
  }

  init() {
    this.fetchBins();
    this.fetchRoutes();
    this.initScenarioSliders();
  }

  async fetchBins() {
    try {
      const resp = await fetch("/api/bins");
      const data = await resp.json();
      if (data.status === "success" && data.bins) {
        this.binsData = data.bins;
        this.renderSmartBinsTable();
        this.updateRadarNodes();
        this.selectBin(this.currentBinCode);
      }
    } catch (err) {
      console.warn("Could not fetch smart bins:", err);
    }
  }

  async fetchRoutes() {
    try {
      const resp = await fetch("/api/routes");
      const data = await resp.json();
      if (data.status === "success" && data.routes) {
        data.routes.forEach(r => {
          const idKey = r.id.toLowerCase().replace(/[^a-z0-9]/g, '');
          const statusEl = document.getElementById(`route-${idKey}-status`);
          const btnEl = document.getElementById(`btn-dispatch-${idKey}`);
          if (statusEl) {
            statusEl.textContent = `Status: ${r.status}`;
            statusEl.style.color = (r.status === "Dispatched" || r.status === "In Transit") ? "var(--brand-neon)" : "var(--text-secondary)";
          }
          if (btnEl) {
            if (r.status === "Dispatched") {
              btnEl.textContent = "Dispatched (Active)";
              btnEl.style.borderColor = "var(--brand-neon)";
              btnEl.style.color = "var(--brand-neon)";
            } else if (r.status === "In Transit") {
              btnEl.textContent = "In Transit (Active)";
              btnEl.style.borderColor = "var(--brand-neon)";
              btnEl.style.color = "var(--brand-neon)";
            } else {
              btnEl.textContent = "Dispatch Route Truck";
            }
          }
        });
      }
    } catch (err) {
      console.warn("Could not fetch routes:", err);
    }
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

    // Highlight node
    document.querySelectorAll(".radar-bin-node").forEach(n => {
      n.classList.toggle("selected", n.getAttribute("data-bin") === binCode);
    });

    // Update inspector
    const elCode = document.getElementById("inspector-bin-code");
    const elName = document.getElementById("inspector-name");
    const elLocation = document.getElementById("inspector-location");
    const elStream = document.getElementById("inspector-stream");
    const elBattery = document.getElementById("inspector-battery");
    const elFillNum = document.getElementById("inspector-fill-num");
    const elFillBar = document.getElementById("inspector-fill-bar");
    const elBadge = document.getElementById("inspector-status-badge");

    if (elCode) elCode.textContent = bin.code;
    if (elName) elName.textContent = bin.name;
    if (elLocation) elLocation.textContent = bin.location;
    if (elStream) elStream.textContent = bin.stream;
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
      elBadge.textContent = bin.status;
      elBadge.className = "tax-pill-badge";
      if (bin.status.toLowerCase().includes("critical")) {
        elBadge.classList.add("tax-pill-red");
      } else if (bin.status.toLowerCase().includes("near")) {
        elBadge.classList.add("tax-pill-orange");
      } else {
        elBadge.classList.add("tax-pill-green");
      }
    }
  }

  async serviceCurrentBin() {
    if (!this.currentBinCode) return;
    try {
      const resp = await fetch(`/api/bins/${this.currentBinCode}/service`, { method: "POST" });
      const data = await resp.json();
      if (data.status === "success") {
        await this.fetchBins();
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast(`Bin ${this.currentBinCode} serviced: Fill level emptied to 0% and alert cleared.`);
        }
      }
    } catch (err) {
      console.error("Error servicing bin:", err);
    }
  }

  async dispatchRoute(routeId) {
    try {
      const resp = await fetch(`/api/routes/${routeId}/dispatch`, { method: "POST" });
      const data = await resp.json();
      if (data.status === "success") {
        await this.fetchRoutes();
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast(`Route ${routeId} successfully dispatched! Status: In Transit.`);
        }
      }
    } catch (err) {
      console.error("Error dispatching route:", err);
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
        }
      } catch (err) {
        console.warn("Error running scenario simulation:", err);
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
