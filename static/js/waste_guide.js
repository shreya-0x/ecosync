/**
 * ECOSYNC — Responsible Citizen Waste Guide Controller
 * Searchable directory of household waste items, 8 canonical categories,
 * and 8-point responsible handling guidance.
 */

class WasteGuide {
  constructor() {
    this.container = document.getElementById("view-guide");
    this.searchInput = document.getElementById("guide-search-input");
    this.localityInput = document.getElementById("guide-locality-input");
    this.categoriesContainer = document.getElementById("guide-categories-grid");
    this.itemsContainer = document.getElementById("guide-items-grid");
    this.resultsCountEl = document.getElementById("guide-results-count");
    this.filterPillsContainer = document.getElementById("guide-filter-pills");

    this.activeCategory = "";
    this.currentQuery = "";
    this.currentLocality = "";
    this.debounceTimer = null;

    this.init();
  }

  init() {
    if (!this.container) return;

    this.fetchCategories();
    this.fetchItems();

    if (this.searchInput) {
      this.searchInput.addEventListener("input", (e) => {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
          this.currentQuery = e.target.value.trim();
          this.fetchItems();
        }, 250);
      });
    }

    if (this.localityInput) {
      this.localityInput.addEventListener("change", (e) => {
        this.currentLocality = e.target.value.trim();
        this.fetchItems();
      });
    }
  }

  async fetchCategories() {
    try {
      const resp = await fetch("/api/waste-guide/categories");
      const data = await resp.json();
      if (data.status === "success") {
        this.renderCategories(data.categories || []);
        this.renderFilterPills(data.categories || []);
      }
    } catch (err) {
      console.error("Error fetching waste categories:", err);
    }
  }

  renderCategories(categories) {
    if (!this.categoriesContainer) return;
    this.categoriesContainer.innerHTML = "";

    categories.forEach((cat) => {
      const card = document.createElement("div");
      card.className = "guide-cat-card";
      card.innerHTML = `
        <div class="guide-cat-header">
          <span class="guide-cat-icon">${cat.icon}</span>
          <span class="guide-bin-badge ${cat.badge_class || 'badge-blue'}">${cat.bin_color}</span>
        </div>
        <h4 class="guide-cat-title">${cat.name}</h4>
        <p class="guide-cat-desc">${cat.short_desc}</p>
        <div class="guide-cat-meta">
          <span>Bin: <strong>${cat.bin_label}</strong></span>
        </div>
      `;

      card.addEventListener("click", () => {
        this.setCategoryFilter(cat.name);
      });

      this.categoriesContainer.appendChild(card);
    });
  }

  renderFilterPills(categories) {
    if (!this.filterPillsContainer) return;
    this.filterPillsContainer.innerHTML = "";

    // "All" pill
    const allPill = document.createElement("button");
    allPill.className = `btn-guide-pill ${this.activeCategory === "" ? "active" : ""}`;
    allPill.textContent = "All Categories";
    allPill.addEventListener("click", () => this.setCategoryFilter(""));
    this.filterPillsContainer.appendChild(allPill);

    categories.forEach((cat) => {
      const pill = document.createElement("button");
      pill.className = `btn-guide-pill ${this.activeCategory === cat.name ? "active" : ""}`;
      pill.innerHTML = `${cat.icon} ${cat.name}`;
      pill.addEventListener("click", () => this.setCategoryFilter(cat.name));
      this.filterPillsContainer.appendChild(pill);
    });
  }

  setCategoryFilter(catName) {
    this.activeCategory = catName;
    document.querySelectorAll(".btn-guide-pill").forEach((btn) => {
      const isMatch = catName === "" 
        ? btn.textContent === "All Categories" 
        : btn.textContent.includes(catName);
      btn.classList.toggle("active", isMatch);
    });
    this.fetchItems();
  }

  async fetchItems() {
    if (!this.itemsContainer) return;
    this.itemsContainer.innerHTML = `<div class="guide-loading">Searching citizen waste guide...</div>`;

    try {
      const params = new URLSearchParams();
      if (this.currentQuery) params.append("q", this.currentQuery);
      if (this.activeCategory) params.append("category", this.activeCategory);
      if (this.currentLocality) params.append("locality", this.currentLocality);

      const resp = await fetch(`/api/waste-guide?${params.toString()}`);
      const data = await resp.json();

      if (data.status === "success") {
        this.renderItems(data.items || []);
        if (this.resultsCountEl) {
          this.resultsCountEl.textContent = `${data.count} item${data.count === 1 ? "" : "s"} found`;
        }
      }
    } catch (err) {
      console.error("Error fetching waste items:", err);
      this.itemsContainer.innerHTML = `<div class="guide-error">Failed to load waste guide items.</div>`;
    }
  }

  renderItems(items) {
    if (!this.itemsContainer) return;
    this.itemsContainer.innerHTML = "";

    if (items.length === 0) {
      this.itemsContainer.innerHTML = `
        <div class="guide-empty-state">
          <div class="empty-icon">🔍</div>
          <h3>No matching items found</h3>
          <p>Try searching for common household items like "bottle", "battery", "cooking oil", or select a category filter.</p>
        </div>
      `;
      return;
    }

    items.forEach((item) => {
      const card = document.createElement("div");
      card.className = "guide-item-card";

      const g = item.guide || {};
      const catInfo = item.category_info || {};

      card.innerHTML = `
        <div class="guide-item-header">
          <div>
            <span class="guide-bin-badge ${catInfo.badge_class || 'badge-blue'}">${catInfo.icon || '📦'} ${item.category}</span>
            <h3 class="guide-item-title">${item.display_name}</h3>
            <span class="guide-item-material">Material: ${item.material}</span>
          </div>
          <button class="btn-toggle-guide-expand" title="Toggle 8-Point Guidance">▼ How to Handle</button>
        </div>

        <div class="guide-quick-summary">
          <div class="guide-summary-row">
            <span class="summary-label">Target Bin:</span>
            <span class="summary-value">${g.which_bin || 'See local rules'}</span>
          </div>
          <div class="guide-summary-row">
            <span class="summary-label">Key Action:</span>
            <span class="summary-value">${g.what_to_do_now || 'Inspect cleanliness'}</span>
          </div>
        </div>

        <!-- Collapsible Full 8-Point Citizen Instructions -->
        <div class="guide-item-details">
          <div class="guide-eight-points">
            <div class="guide-point-box">
              <div class="point-num">1. What is it?</div>
              <div class="point-text">${g.what_is_it || ''}</div>
            </div>
            <div class="guide-point-box highlight">
              <div class="point-num">2. What should I do now?</div>
              <div class="point-text">${g.what_to_do_now || ''}</div>
            </div>
            <div class="guide-point-box">
              <div class="point-num">3. Which bin should I use?</div>
              <div class="point-text"><strong>${g.which_bin || ''}</strong></div>
            </div>
            <div class="guide-point-box">
              <div class="point-num">4. How should I prepare it?</div>
              <div class="point-text">${g.how_to_prepare || ''}</div>
            </div>
            <div class="guide-point-box warning">
              <div class="point-num">5. What should I avoid?</div>
              <div class="point-text">${g.what_to_avoid || ''}</div>
            </div>
            <div class="guide-point-box">
              <div class="point-num">6. Where should it go?</div>
              <div class="point-text">${g.where_should_it_go || ''}</div>
            </div>
            <div class="guide-point-box">
              <div class="point-num">7. Why does this matter?</div>
              <div class="point-text">${g.why_matters || ''}</div>
            </div>
            <div class="guide-point-box action">
              <div class="point-num">8. Good-Citizen Action:</div>
              <div class="point-text">${g.citizen_action || ''}</div>
            </div>
          </div>

          <div class="guide-item-footer">
            <button class="btn-primary-sm btn-guide-scan-match">📷 Scan This With Camera</button>
            <button class="btn-secondary-sm btn-guide-ask-ai" data-item="${item.display_name}">💬 Ask AI Advisor</button>
          </div>
        </div>
      `;

      // Expand / Collapse
      const toggleBtn = card.querySelector(".btn-toggle-guide-expand");
      const detailsEl = card.querySelector(".guide-item-details");
      toggleBtn.addEventListener("click", () => {
        const isOpen = detailsEl.classList.toggle("open");
        toggleBtn.textContent = isOpen ? "▲ Close Guidance" : "▼ How to Handle";
      });

      // Actions
      card.querySelector(".btn-guide-scan-match").addEventListener("click", () => {
        if (window.ecosyncApp) {
          window.ecosyncApp.switchView("scanner");
        }
      });

      card.querySelector(".btn-guide-ask-ai").addEventListener("click", () => {
        if (window.aiAdvisor) {
          window.aiAdvisor.openWithPrompt(`How should I handle and dispose of ${item.display_name}?`);
        }
      });

      this.itemsContainer.appendChild(card);
    });
  }
}

window.WasteGuide = WasteGuide;
