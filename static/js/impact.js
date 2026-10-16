/**
 * ECOSYNC — Household Impact & History Controller
 * Renders personal household metrics, category distributions,
 * avoided carbon emissions, relatable equivalencies, and genuine activity history.
 */

class HouseholdImpact {
  constructor() {
    this.container = document.getElementById("view-impact");
    this.metricScans = document.getElementById("impact-total-scans");
    this.metricConfirmed = document.getElementById("impact-total-confirmed");
    this.metricDiverted = document.getElementById("impact-diverted-kg");
    this.metricCo2 = document.getElementById("impact-avoided-co2");
    this.metricEnergy = document.getElementById("impact-energy-saved");

    // Human equivalencies
    this.equivCars = document.getElementById("impact-equiv-cars");
    this.equivPhones = document.getElementById("impact-equiv-phones");
    this.equivBulbs = document.getElementById("impact-equiv-bulbs");

    this.categoryBarsContainer = document.getElementById("impact-category-bars");
    this.actionBarsContainer = document.getElementById("impact-action-bars");
    this.historyTableBody = document.getElementById("impact-history-tbody");

    this.init();
  }

  init() {
    if (!this.container) return;
    this.initFilterEvents();
  }

  initFilterEvents() {
    const searchInput = document.getElementById("history-search-input");
    const categorySelect = document.getElementById("history-category-select");
    const demoSelect = document.getElementById("history-filter-demo");
    const refreshBtn = document.getElementById("btn-refresh-history");

    const doFilter = () => {
      const q = searchInput ? searchInput.value : "";
      const cat = categorySelect ? categorySelect.value : "";
      const isDemo = demoSelect ? demoSelect.value : "";
      this.fetchHistory(q, cat, isDemo);
    };

    if (searchInput) searchInput.addEventListener("input", () => doFilter());
    if (categorySelect) categorySelect.addEventListener("change", () => doFilter());
    if (demoSelect) demoSelect.addEventListener("change", () => doFilter());
    if (refreshBtn) refreshBtn.addEventListener("click", () => doFilter());
  }

  async fetchImpactMetrics() {
    try {
      const resp = await fetch("/api/household/impact");
      const data = await resp.json();
      if (data.status === "success") {
        this.renderMetrics(data);
      }
    } catch (err) {
      console.error("Error loading household impact metrics:", err);
    }
  }

  renderMetrics(data) {
    const m = data.household_metrics || {};

    const scans = m.total_scans_performed || 0;
    const confirmed = m.total_items_confirmed || 0;
    const divertedKg = m.diverted_weight_kg || 0;
    const co2Kg = m.avoided_ghg_emissions_kg_co2e || 0;
    const energyKwh = m.energy_saved_kwh || 0;

    if (this.metricScans) this.metricScans.textContent = scans;
    if (this.metricConfirmed) this.metricConfirmed.textContent = confirmed;
    if (this.metricDiverted) this.metricDiverted.textContent = `${divertedKg} kg`;
    if (this.metricCo2) this.metricCo2.textContent = `${co2Kg} kg`;
    if (this.metricEnergy) this.metricEnergy.textContent = `${energyKwh} kWh`;

    // Calculate tangible human-scale equivalencies
    if (this.equivCars) {
      const carKm = (co2Kg * 4.1).toFixed(1);
      this.equivCars.textContent = `${carKm} km`;
    }
    if (this.equivPhones) {
      const phoneCharges = Math.round(energyKwh * 80);
      this.equivPhones.textContent = `${phoneCharges} charges`;
    }
    if (this.equivBulbs) {
      const bulbHours = Math.round(energyKwh * 110);
      this.equivBulbs.textContent = `${bulbHours} hours`;
    }

    // Render category distribution bars
    if (this.categoryBarsContainer) {
      this.categoryBarsContainer.innerHTML = "";
      const catCounts = m.category_distribution || {};
      const total = Object.values(catCounts).reduce((a, b) => a + b, 0) || 1;

      if (Object.keys(catCounts).length === 0) {
        this.categoryBarsContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No confirmed items yet. Scan an item to see category breakdown.</p>`;
      } else {
        Object.entries(catCounts).forEach(([cat, count]) => {
          const pct = Math.round((count / total) * 100);
          const wt = (m.category_weights_kg || {})[cat] || 0;
          const row = document.createElement("div");
          row.className = "impact-distribution-row";
          row.innerHTML = `
            <div class="row-label-wrap">
              <span class="row-label">${cat}</span>
              <span class="row-count">${count} items (${wt} kg)</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill fill-green" style="width: ${pct}%"></div>
            </div>
          `;
          this.categoryBarsContainer.appendChild(row);
        });
      }
    }

    // Render action distribution
    if (this.actionBarsContainer) {
      this.actionBarsContainer.innerHTML = "";
      const actions = m.actions_distribution || {};
      const totalActs = Object.values(actions).reduce((a, b) => a + b, 0) || 1;

      if (Object.keys(actions).length === 0) {
        this.actionBarsContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No recorded disposal actions yet.</p>`;
      } else {
        Object.entries(actions).forEach(([act, count]) => {
          const pct = Math.round((count / totalActs) * 100);
          const row = document.createElement("div");
          row.className = "impact-distribution-row";
          row.innerHTML = `
            <div class="row-label-wrap">
              <span class="row-label">${act}</span>
              <span class="row-count">${count} items (${pct}%)</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill fill-blue" style="width: ${pct}%"></div>
            </div>
          `;
          this.actionBarsContainer.appendChild(row);
        });
      }
    }
  }

  async fetchHistory(search = "", category = "", isDemo = "") {
    if (!this.historyTableBody) return;
    try {
      const params = new URLSearchParams({ limit: "50" });
      if (search) params.append("search", search);
      if (category) params.append("category", category);
      if (isDemo !== "") params.append("is_demo", isDemo);

      const resp = await fetch(`/api/history?${params.toString()}`);
      const data = await resp.json();
      if (data.status === "success") {
        this.renderHistoryTable(data.history || []);
      }
    } catch (err) {
      console.error("Error loading activity history:", err);
    }
  }

  renderHistoryTable(records) {
    if (!this.historyTableBody) return;
    this.historyTableBody.innerHTML = "";

    if (records.length === 0) {
      this.historyTableBody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; padding: 24px; color: var(--text-muted);">
            No records matched your search. Scan waste items using your camera to log real actions!
          </td>
        </tr>
      `;
      return;
    }

    records.forEach((rec) => {
      const tr = document.createElement("tr");
      const dateStr = rec.created_at ? new Date(rec.created_at).toLocaleString() : "Recent";
      const isDemo = rec.is_demo === 1;

      const recordTypeBadge = isDemo
        ? `<span style="display:inline-block; font-size:10px; font-weight:800; padding:2px 7px; border-radius:4px; background:#fef3c7; color:#92400e; border: 1px solid #fde68a;">DEMO DATA</span>`
        : `<span style="display:inline-block; font-size:10px; font-weight:800; padding:2px 7px; border-radius:4px; background:#d1fae5; color:#065f46; border: 1px solid #a7f3d0;">VERIFIED CITIZEN</span>`;

      tr.innerHTML = `
        <td><strong style="font-family: var(--font-mono); font-size: 11.5px;">${rec.id}</strong></td>
        <td><strong>${rec.item_name}</strong></td>
        <td><span style="display:inline-block; font-size:11px; font-weight:700; padding:2px 8px; border-radius:9999px; background:#eff6ff; color:#1e40af;">${rec.category}</span></td>
        <td><span style="display:inline-block; font-size:11px; font-weight:700; padding:2px 8px; border-radius:9999px; background:#f0fdf4; color:#166534;">${rec.action_taken}</span></td>
        <td>${rec.estimated_weight_kg} kg</td>
        <td>${recordTypeBadge}</td>
        <td style="color: var(--text-muted); font-size: 11.5px;">${dateStr}</td>
      `;
      this.historyTableBody.appendChild(tr);
    });
  }
}

window.HouseholdImpact = HouseholdImpact;
