/**
 * ECOSYNC — Analytics & Environmental Impact Controller
 * Matches Reference Images 19 and 23.
 */

class HouseholdImpact {
  constructor() {
    this.kpiScans = document.getElementById("kpi-scans-count");
    this.kpiObjects = document.getElementById("kpi-objects-count");
    this.kpiDryShare = document.getElementById("kpi-dry-share");
    this.kpiCo2 = document.getElementById("kpi-co2e-offset");
    this.historyTableBody = document.getElementById("impact-history-tbody");

    this.init();
  }

  init() {
    this.fetchImpactMetrics();
    this.fetchHistory();
  }

  async fetchImpactMetrics() {
    try {
      const resp = await fetch("/api/household/impact");
      const data = await resp.json();
      if (data.status === "success") {
        const m = data.household_metrics || {};
        const scans = m.total_scans_performed || 0;
        const confirmed = m.total_items_confirmed || 0;
        const co2 = m.avoided_ghg_emissions_kg_co2e || 0;

        if (this.kpiScans) this.kpiScans.textContent = scans;
        if (this.kpiObjects) this.kpiObjects.textContent = confirmed;
        if (this.kpiCo2) this.kpiCo2.textContent = `${co2} kg`;

        // Calculate dry-stream share
        const catDist = m.category_distribution || {};
        const dryCount = (catDist["Recyclable materials"] || 0) + (catDist["Municipal solid waste"] || 0) + (catDist["Electronic waste"] || 0);
        const totalCount = Object.values(catDist).reduce((a, b) => a + b, 0) || 1;
        const dryPct = totalCount > 0 ? ((dryCount / totalCount) * 100).toFixed(1) : "0.0";
        if (this.kpiDryShare) this.kpiDryShare.textContent = `${dryPct}%`;
      }
    } catch (err) {
      console.warn("Error fetching analytics metrics:", err);
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
      console.warn("Error loading activity history:", err);
    }
  }

  renderHistoryTable(records) {
    if (!this.historyTableBody) return;
    this.historyTableBody.innerHTML = "";

    if (records.length === 0) {
      this.historyTableBody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; padding: 30px; color: var(--text-muted); font-size:14px;">
            No scan events recorded yet. Run a scan in the AI Vision Studio to generate persistent records!
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
        ? `<span class="tax-pill-badge tax-pill-orange">DEMO DATA</span>`
        : `<span class="tax-pill-badge tax-pill-green">VERIFIED CITIZEN</span>`;

      tr.innerHTML = `
        <td style="font-family:var(--font-mono); font-size:12px; color:var(--brand-neon); font-weight:700;">${rec.id}</td>
        <td style="font-weight:600; color:#fff;">${rec.item_name}</td>
        <td><span class="tax-pill-badge tax-pill-blue">${rec.category}</span></td>
        <td style="font-size:13px; color:var(--text-secondary);">${rec.material || 'N/A'}</td>
        <td style="font-family:var(--font-mono);">${Math.round((rec.confidence || 0.9) * 100)}%</td>
        <td>${recordTypeBadge}</td>
        <td style="color:var(--text-muted); font-size:12px;">${dateStr}</td>
      `;
      this.historyTableBody.appendChild(tr);
    });
  }

  exportCSV() {
    window.location.href = "/api/history/export";
    if (window.showEcoSyncToast) {
      window.showEcoSyncToast("Downloading RFC-4180 compliant verified CSV report...");
    }
  }
}

window.householdImpact = new HouseholdImpact();
window.ecosyncImpact = window.householdImpact;
