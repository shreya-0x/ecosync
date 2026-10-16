/**
 * ECOSYNC — Analytics Dashboard & Transparent Environmental Impact Calculations
 * Derived from real SQLite records and EPA WARM v15 conversion indices.
 */

class AnalyticsDashboard {
  constructor() {
    this.filterMaterial = document.getElementById("analytics-filter-material");
    this.filterFacility = document.getElementById("analytics-filter-facility");
    this.filterStatus = document.getElementById("analytics-filter-status");
    this.toggleSimulated = document.getElementById("analytics-include-simulated");

    // Headline metrics elements
    this.elTotalWeight = document.getElementById("metric-total-weight");
    this.elTotalBatches = document.getElementById("metric-total-batches");
    this.elRecoveryRate = document.getElementById("metric-recovery-rate");
    this.elDivertedLandfill = document.getElementById("metric-diverted-landfill");

    // Impact metrics
    this.elAvoidedCo2 = document.getElementById("metric-avoided-co2");
    this.elEnergySaved = document.getElementById("metric-energy-saved");
    this.elVirginOffset = document.getElementById("metric-virgin-offset");

    // Charts
    this.materialChartContainer = document.getElementById("chart-materials-distribution");
    this.pipelineChartContainer = document.getElementById("chart-lifecycle-pipeline");

    this.init();
  }

  init() {
    this.initFilterEvents();
    this.fetchAnalytics();
  }

  initFilterEvents() {
    const filters = [this.filterMaterial, this.filterFacility, this.filterStatus, this.toggleSimulated];
    filters.forEach((f) => {
      if (f) {
        f.addEventListener("change", () => this.fetchAnalytics());
      }
    });
  }

  async fetchAnalytics() {
    const params = new URLSearchParams();
    if (this.filterMaterial && this.filterMaterial.value) {
      params.append("material", this.filterMaterial.value);
    }
    if (this.filterFacility && this.filterFacility.value) {
      params.append("facility", this.filterFacility.value);
    }
    if (this.filterStatus && this.filterStatus.value) {
      params.append("status", this.filterStatus.value);
    }
    if (this.toggleSimulated) {
      params.append("include_simulated", this.toggleSimulated.checked ? "1" : "0");
    }

    try {
      const resp = await fetch(`/api/analytics?${params.toString()}`);
      const data = await resp.json();
      if (data.status === "success") {
        this.renderMetrics(data);
        this.renderMaterialDistributionChart(data.material_distribution || {});
        this.renderPipelineFunnelChart(data.status_distribution || {});
      }
    } catch (err) {
      console.error("Error loading analytics:", err);
    }
  }

  renderMetrics(data) {
    const h = data.headline_metrics;
    const env = data.environmental_impact;

    if (this.elTotalWeight) this.elTotalWeight.textContent = `${h.total_weight_kg.toLocaleString()} kg`;
    if (this.elTotalBatches) this.elTotalBatches.textContent = h.total_batches_tracked;
    if (this.elRecoveryRate) this.elRecoveryRate.textContent = `${h.recovery_rate_pct}%`;
    if (this.elDivertedLandfill) this.elDivertedLandfill.textContent = `${env.landfill_diverted_volume_m3} m³`;

    if (this.elAvoidedCo2) this.elAvoidedCo2.textContent = `${env.avoided_ghg_emissions_mt_co2e} MT CO₂e`;
    if (this.elEnergySaved) this.elEnergySaved.textContent = `${env.energy_saved_kwh.toLocaleString()} kWh`;
    if (this.elVirginOffset) this.elVirginOffset.textContent = `${env.virgin_material_offset_kg.toLocaleString()} kg`;
  }

  renderMaterialDistributionChart(materials) {
    if (!this.materialChartContainer) return;
    const entries = Object.entries(materials);

    if (!entries.length) {
      this.materialChartContainer.innerHTML = "<div style='color: var(--text-muted); padding: 40px; text-align: center; font-size: 12px;'>No material records matching filter criteria.</div>";
      return;
    }

    const totalWeight = entries.reduce((acc, [_, item]) => acc + item.weight_kg, 0);

    const colors = {
      "Plastic": "#86efac",
      "Metal": "#fb923c",
      "Paper": "#fcd34d",
      "Cardboard": "#f59e0b",
      "Glass": "#60a5fa",
      "Electronic Waste": "#c084fc",
      "General / Unmapped": "#94a3b8"
    };

    let barsHtml = entries.map(([name, item]) => {
      const pct = totalWeight > 0 ? Math.round((item.weight_kg / totalWeight) * 100) : 0;
      const color = colors[name] || "#86efac";

      return `
        <div style="margin-bottom: 14px; font-family: var(--font-mono); font-size: 11px;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span><strong style="color: ${color};">■</strong> ${name}</span>
            <span>${item.weight_kg.toLocaleString()} kg (${pct}%)</span>
          </div>
          <div style="width: 100%; height: 6px; background: var(--bg-surface-elevated); border-radius: 2px; overflow: hidden;">
            <div style="width: ${pct}%; height: 100%; background: ${color}; transition: width 0.5s ease;"></div>
          </div>
        </div>
      `;
    }).join("");

    this.materialChartContainer.innerHTML = barsHtml;
  }

  renderPipelineFunnelChart(statuses) {
    if (!this.pipelineChartContainer) return;

    const stages = ["Detected", "Classified", "Verified", "Collected", "Sorted", "Processed"];
    const maxCount = Math.max(...stages.map((st) => statuses[st] || 0), 1);

    let funnelHtml = stages.map((st) => {
      const count = statuses[st] || 0;
      const pct = Math.round((count / maxCount) * 100);

      return `
        <div style="margin-bottom: 12px; font-family: var(--font-mono); font-size: 11px;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: var(--text-secondary);">${st.toUpperCase()}</span>
            <span style="color: var(--accent-lime); font-weight: 700;">${count} BATCHES</span>
          </div>
          <div style="width: 100%; height: 6px; background: var(--bg-surface-elevated); border-radius: 2px; overflow: hidden;">
            <div style="width: ${pct}%; height: 100%; background: var(--accent-lime); opacity: ${0.4 + (pct / 100) * 0.6}; transition: width 0.5s ease;"></div>
          </div>
        </div>
      `;
    }).join("");

    this.pipelineChartContainer.innerHTML = funnelHtml;
  }
}

window.AnalyticsDashboard = AnalyticsDashboard;
