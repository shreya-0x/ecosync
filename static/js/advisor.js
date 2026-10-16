/**
 * ECOSYNC — Explainable AI Advisor Controller
 * Live operational insights, bottleneck alerts, and grounded circular economy query console.
 */

class AIAdvisor {
  constructor() {
    this.insightsFeed = document.getElementById("advisor-insights-feed");
    this.chatLog = document.getElementById("advisor-chat-log");
    this.inputField = document.getElementById("advisor-query-input");
    this.btnSubmit = document.getElementById("btn-submit-advisor-query");
    this.suggestedChips = document.querySelectorAll(".advisor-chip-prompt");

    this.init();
  }

  init() {
    this.fetchInsights();

    if (this.btnSubmit && this.inputField) {
      this.btnSubmit.addEventListener("click", () => this.handleQuerySubmit());
      this.inputField.addEventListener("keydown", (e) => {
        if (e.key === "Enter") this.handleQuerySubmit();
      });
    }

    if (this.suggestedChips) {
      this.suggestedChips.forEach((chip) => {
        chip.addEventListener("click", (e) => {
          const text = e.currentTarget.textContent.trim();
          if (this.inputField) {
            this.inputField.value = text;
            this.handleQuerySubmit();
          }
        });
      });
    }
  }

  openWithPrompt(promptText) {
    if (window.ecosyncApp) {
      window.ecosyncApp.switchView("advisor");
    }
    if (this.inputField) {
      this.inputField.value = promptText;
      setTimeout(() => this.handleQuerySubmit(), 200);
    }
  }

  async fetchInsights() {
    if (!this.insightsFeed) return;

    try {
      const resp = await fetch("/api/advisor/insights");
      const data = await resp.json();
      if (data.status === "success") {
        this.renderInsights(data.insights || []);
      }
    } catch (err) {
      console.error("Error loading advisor insights:", err);
    }
  }

  renderInsights(insights) {
    if (!this.insightsFeed) return;
    this.insightsFeed.innerHTML = "";

    if (!insights.length) {
      this.insightsFeed.innerHTML = "<div style='color: var(--text-muted); font-size: 12px; padding: 12px;'>No active operational alerts or bottlenecks.</div>";
      return;
    }

    insights.forEach((item) => {
      const card = document.createElement("div");
      card.className = `insight-card-item ${item.level}`;

      card.innerHTML = `
        <div style="font-family: var(--font-mono); font-size: 10px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 2px;">
          ${item.category}
        </div>
        <div class="insight-card-title">${item.title}</div>
        <div class="insight-card-summary">${item.summary}</div>
        <div style="margin-top: 8px; font-family: var(--font-mono); font-size: 11px; color: var(--accent-lime);">
          > Recommended Action: ${item.action_suggested}
        </div>
      `;

      this.insightsFeed.appendChild(card);
    });
  }

  async handleQuerySubmit() {
    if (!this.inputField) return;
    const q = this.inputField.value.trim();
    if (!q) return;

    this.inputField.value = "";

    // 1. Append user message
    this.appendMessage("user", q);

    // 2. Append loading indicator
    const loadingId = this.appendLoadingMessage();

    try {
      const resp = await fetch("/api/advisor/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q })
      });
      const data = await resp.json();

      this.removeLoadingMessage(loadingId);

      if (data.status === "success") {
        this.appendMessage("assistant", data.data.answer, data.data.source);
      } else {
        this.appendMessage("assistant", "Error: " + (data.message || "Failed to process question."));
      }
    } catch (err) {
      this.removeLoadingMessage(loadingId);
      console.error("Query submission error:", err);
      this.appendMessage("assistant", "Network error: Unable to connect to the EcoSync Advisory Engine.");
    }
  }

  appendMessage(role, text, source) {
    if (!this.chatLog) return;

    const bubble = document.createElement("div");
    bubble.className = `advisor-message-bubble ${role}`;

    let sourceHtml = "";
    if (source) {
      sourceHtml = `<div class="advisor-source-tag">${source}</div>`;
    }

    // Basic markdown parsing for boldness and line breaks
    const formatted = text
      .replace(/### (.*?)\n/g, '<h4 style="font-family: var(--font-display); font-size: 15px; margin: 8px 0 4px 0; text-transform: uppercase;">$1</h4>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n- (.*?)/g, '<div style="margin-left: 12px;">• $1</div>')
      .replace(/\n\n/g, '<br><br>');

    bubble.innerHTML = `${sourceHtml}<div>${formatted}</div>`;
    this.chatLog.appendChild(bubble);
    this.chatLog.scrollTop = this.chatLog.scrollHeight;
  }

  appendLoadingMessage() {
    const id = "loading-" + Date.now();
    const bubble = document.createElement("div");
    bubble.id = id;
    bubble.className = "advisor-message-bubble assistant";
    bubble.innerHTML = "<span style='font-family: var(--font-mono); font-size: 12px; color: var(--accent-lime);'>ANALYZING LIVE TELEMETRY & CIRCULAR PROTOCOLS...</span>";
    this.chatLog.appendChild(bubble);
    this.chatLog.scrollTop = this.chatLog.scrollHeight;
    return id;
  }

  removeLoadingMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }
}

window.AIAdvisor = AIAdvisor;
