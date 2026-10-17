/**
 * ECOSYNC — Sustainability Advisor (17 Classes) & Circular Guide
 * Matches Reference Image 7 and all circular handbook features.
 */

const ADVISOR_17_CLASSES = [
  {
    id: "redbull_can",
    title: "Redbull can (dry waste)",
    stream: "DRY WASTE",
    streamColor: "#60a5fa",
    streamBg: "#0e2246",
    bin: "Blue Bin (Recyclables)",
    prep: "Rinse out residual liquid and crush. 100% infinitely recyclable.",
    co2: "~0.12 kg CO2e",
    tags: ["metals", "dry"]
  },
  {
    id: "apple",
    title: "apple (wet waste)",
    stream: "WET WASTE",
    streamColor: "#4ade80",
    streamBg: "#0b2e1b",
    bin: "Green Bin (Compost)",
    prep: "Deposit in wet waste/compost. Decomposes into organic fertilizer.",
    co2: "~0.05 kg CO2e",
    tags: ["wet"]
  },
  {
    id: "banana",
    title: "banana (wet waste)",
    stream: "WET WASTE",
    streamColor: "#4ade80",
    streamBg: "#0b2e1b",
    bin: "Green Bin (Compost)",
    prep: "Deposit in wet waste/compost. Rich in potassium and rapid bio-degradation.",
    co2: "~0.05 kg CO2e",
    tags: ["wet"]
  },
  {
    id: "bottle",
    title: "bottles (dry waste)",
    stream: "DRY WASTE",
    streamColor: "#60a5fa",
    streamBg: "#0e2246",
    bin: "Blue Bin (Dry Recyclables)",
    prep: "Empty liquid, compress to save bin space, cap tightly.",
    co2: "~0.08 kg CO2e",
    tags: ["plastics", "dry"]
  },
  {
    id: "cucumber",
    title: "cucumber (wet waste)",
    stream: "WET WASTE",
    streamColor: "#4ade80",
    streamBg: "#0b2e1b",
    bin: "Green Bin (Compost)",
    prep: "Compostable organic matter. Keep separate from synthetic packaging.",
    co2: "~0.05 kg CO2e",
    tags: ["wet"]
  },
  {
    id: "dairy_milk",
    title: "dairy milk (wet waste)",
    stream: "WET WASTE",
    streamColor: "#4ade80",
    streamBg: "#0b2e1b",
    bin: "Green Bin (Wet Waste)",
    prep: "Food scrap/chocolate residue goes to wet waste; clean foil wrapper to dry.",
    co2: "~0.06 kg CO2e",
    tags: ["wet", "plastics"]
  },
  {
    id: "doritos",
    title: "doritos (dry waste)",
    stream: "DRY WASTE",
    streamColor: "#60a5fa",
    streamBg: "#0e2246",
    bin: "Blue Bin (Dry Waste)",
    prep: "Empty crumbs. Multi-layer packaging goes to dry waste for energy recovery.",
    co2: "~0.03 kg CO2e",
    tags: ["plastics", "dry"]
  },
  {
    id: "glass_materials",
    title: "glass materials (dry waste)",
    stream: "DRY WASTE",
    streamColor: "#60a5fa",
    streamBg: "#0e2246",
    bin: "Blue Bin (Glass Recycling)",
    prep: "Rinse clean. Deposit gently to prevent broken glass hazards.",
    co2: "~0.15 kg CO2e",
    tags: ["dry"]
  },
  {
    id: "cardboard",
    title: "cardboard packaging (dry waste)",
    stream: "DRY WASTE",
    streamColor: "#60a5fa",
    streamBg: "#0e2246",
    bin: "Blue Bin (Paper/Cardboard)",
    prep: "Flatten boxes completely to conserve bin volume. Remove plastic tape.",
    co2: "~0.18 kg CO2e",
    tags: ["dry"]
  },
  {
    id: "alum_can",
    title: "aluminum beverage can (dry waste)",
    stream: "DRY WASTE",
    streamColor: "#60a5fa",
    streamBg: "#0e2246",
    bin: "Blue Bin (Metals)",
    prep: "Rinse empty and crush flat. Remelt uses 95% less energy than virgin mining.",
    co2: "~0.14 kg CO2e",
    tags: ["metals", "dry"]
  },
  {
    id: "plastic_container",
    title: "plastic food container (dry waste)",
    stream: "DRY WASTE",
    streamColor: "#60a5fa",
    streamBg: "#0e2246",
    bin: "Blue Bin (Plastics)",
    prep: "Wash off residual grease and food oil with a 5-second rinse before binning.",
    co2: "~0.09 kg CO2e",
    tags: ["plastics", "dry"]
  },
  {
    id: "batteries",
    title: "household batteries (hazardous)",
    stream: "HAZARDOUS",
    streamColor: "#f87171",
    streamBg: "#2e0e0e",
    bin: "Red Bin (Hazardous Depot)",
    prep: "Tape terminals with clear scotch tape to prevent friction fires in bins.",
    co2: "~0.22 kg CO2e",
    tags: ["ewaste"]
  },
  {
    id: "cables",
    title: "electronic cables & e-waste",
    stream: "E-WASTE",
    streamColor: "#fbbf24",
    streamBg: "#2f1d06",
    bin: "Orange Hub (E-Waste)",
    prep: "Copper extraction and certified electronic reclamation. Keep out of curbside bins.",
    co2: "~0.25 kg CO2e",
    tags: ["ewaste"]
  },
  {
    id: "food_leftovers",
    title: "food leftovers & peels (wet waste)",
    stream: "WET WASTE",
    streamColor: "#4ade80",
    streamBg: "#0b2e1b",
    bin: "Green Bin (Compost)",
    prep: "Layer kitchen trimmings with dry brown leaves or newspaper to avoid odor.",
    co2: "~0.06 kg CO2e",
    tags: ["wet"]
  },
  {
    id: "paper_cup",
    title: "disposable paper cup (dry waste)",
    stream: "DRY WASTE",
    streamColor: "#94a3b8",
    streamBg: "#1e293b",
    bin: "Gray Bin (General Trash)",
    prep: "Poly-coated interior plastic barrier requires specialized cup pulping.",
    co2: "~0.02 kg CO2e",
    tags: ["dry"]
  },
  {
    id: "styrofoam",
    title: "styrofoam & bubble wrap (dry waste)",
    stream: "DRY WASTE",
    streamColor: "#94a3b8",
    streamBg: "#1e293b",
    bin: "Gray / Special Packaging Depot",
    prep: "Bag separately to avoid crumbling into lightweight microplastic beads.",
    co2: "~0.04 kg CO2e",
    tags: ["plastics", "dry"]
  },
  {
    id: "medicines",
    title: "expired medicines & blister packs",
    stream: "HAZARDOUS",
    streamColor: "#f87171",
    streamBg: "#2e0e0e",
    bin: "Red / Pharmacy Drop-off",
    prep: "Take to pharmacy return kiosk. Never flush antibiotics down toilets or drains.",
    co2: "~0.10 kg CO2e",
    tags: ["ewaste"]
  }
];

class WasteGuide {
  constructor() {
    this.cardsContainer = document.getElementById("advisor-cards-container");
    this.filterBar = document.getElementById("advisor-filter-bar");
    this.currentFilter = "all";
    this.init();
  }

  init() {
    this.renderAdvisorCards();
    this.initFilterEvents();
    this.initChecklist();
  }

  initFilterEvents() {
    if (!this.filterBar) return;
    this.filterBar.querySelectorAll(".btn-advisor-filter").forEach(btn => {
      btn.addEventListener("click", (e) => {
        this.filterBar.querySelectorAll(".btn-advisor-filter").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.currentFilter = btn.getAttribute("data-filter");
        this.renderAdvisorCards();
      });
    });
  }

  fetchItems(query = "") {
    if (query && typeof query === "string" && query.trim()) {
      const q = query.toLowerCase().trim();
      const matched = ADVISOR_17_CLASSES.filter(c => 
        c.title.toLowerCase().includes(q) || 
        c.stream.toLowerCase().includes(q) || 
        c.bin.toLowerCase().includes(q) || 
        (c.tags && c.tags.some(t => t.toLowerCase().includes(q)))
      );
      this.renderAdvisorCards(matched);
    } else {
      this.renderAdvisorCards();
    }
  }

  renderAdvisorCards(itemsList = null) {
    if (!this.cardsContainer) return;
    this.cardsContainer.innerHTML = "";

    const items = itemsList || (this.currentFilter === "all"
      ? ADVISOR_17_CLASSES
      : ADVISOR_17_CLASSES.filter(c => c.tags.includes(this.currentFilter)));

    if (!items.length) {
      this.cardsContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted);">
          No waste classes match your current search filter.
        </div>
      `;
      return;
    }

    items.forEach(item => {
      const card = document.createElement("div");
      card.className = "advisor-class-card";
      card.innerHTML = `
        <div class="advisor-card-top">
          <h4 class="advisor-card-title">${item.title}</h4>
          <span class="advisor-stream-tag" style="color:${item.streamColor}; background:${item.streamBg};">${item.stream}</span>
        </div>
        <div class="advisor-bin-dest">${item.bin}</div>
        <p class="advisor-prep-copy">${item.prep}</p>
        <div class="advisor-co2-estimate">Configured estimate: ${item.co2}</div>
      `;
      this.cardsContainer.appendChild(card);
    });
  }

  initChecklist() {
    const group = document.getElementById("checklist-items-group");
    const counterText = document.getElementById("checklist-counter-text");
    const progressBar = document.getElementById("checklist-progress-bar");
    const btnReset = document.getElementById("btn-reset-checklist");

    if (!group) return;

    const saved = JSON.parse(localStorage.getItem("ecosync_checklist") || "{}");

    const updateChecklistUI = () => {
      const rows = group.querySelectorAll(".checklist-item-row");
      let completed = 0;

      rows.forEach((row, idx) => {
        const cb = row.querySelector(".checklist-checkbox");
        const isDone = !!saved[idx];
        if (cb) cb.checked = isDone;
        row.classList.toggle("completed", isDone);
        if (isDone) completed++;
      });

      const total = rows.length;
      const pct = Math.round((completed / total) * 100);
      if (counterText) counterText.textContent = `${completed} of ${total} Completed (${pct}%)`;
      if (progressBar) progressBar.style.width = `${pct}%`;

      localStorage.setItem("ecosync_checklist", JSON.stringify(saved));
    };

    group.querySelectorAll(".checklist-item-row").forEach((row, idx) => {
      const cb = row.querySelector(".checklist-checkbox");
      row.addEventListener("click", (e) => {
        if (e.target !== cb) {
          cb.checked = !cb.checked;
        }
        saved[idx] = cb.checked;
        updateChecklistUI();
      });
    });

    if (btnReset) {
      btnReset.addEventListener("click", () => {
        for (let k in saved) delete saved[k];
        updateChecklistUI();
      });
    }

    updateChecklistUI();
  }
}

window.wasteGuide = new WasteGuide();
