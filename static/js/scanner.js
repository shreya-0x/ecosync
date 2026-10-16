/**
 * ECOSYNC — Smart Waste Scanner & Responsible Citizen Guidance Controller
 * Real YOLO computer-vision inference, aspect-ratio preserved bounding overlays,
 * 8-category taxonomy mapping, 8-point citizen guidance, and honest uncertainty handling.
 */

class WasteScanner {
  constructor() {
    this.dropzone = document.getElementById("scanner-dropzone");
    this.fileInput = document.getElementById("scanner-file-input");
    this.imgDisplay = document.getElementById("bbox-image-display");
    this.overlayCanvas = document.getElementById("bbox-overlay-canvas");
    this.ctx = this.overlayCanvas ? this.overlayCanvas.getContext("2d") : null;
    this.stageContainer = document.getElementById("bbox-stage-container");

    this.resultsPanel = document.getElementById("scanner-results-panel");
    this.detectionsList = document.getElementById("detections-items-list");
    this.countTitle = document.getElementById("detections-count-title");
    this.categoryBadgesWrap = document.getElementById("category-summary-badges");

    this.confSlider = document.getElementById("scanner-conf-slider");
    this.confValueText = document.getElementById("scanner-conf-val-text");
    this.toggleBoxes = document.getElementById("toggle-show-boxes");
    this.toggleLabels = document.getElementById("toggle-show-labels");

    // Camera elements
    this.btnToggleCamera = document.getElementById("btn-toggle-camera");
    this.cameraContainer = document.getElementById("camera-viewfinder-container");
    this.cameraVideo = document.getElementById("camera-video-stream");
    this.btnCaptureCamera = document.getElementById("btn-capture-frame");
    this.btnPauseCamera = document.getElementById("btn-pause-camera");
    this.btnStopCamera = document.getElementById("btn-stop-camera");
    this.cameraStream = null;
    this.isCameraPaused = false;

    // Guidance and confirmation elements
    this.guidanceCard = document.getElementById("scanner-guidance-card");
    this.confirmForm = document.getElementById("scanner-confirmation-form");
    this.selectCategory = document.getElementById("confirm-material-category");
    this.selectAction = document.getElementById("confirm-disposal-action");
    this.inputItemName = document.getElementById("confirm-item-name");
    this.inputWeight = document.getElementById("confirm-weight-kg");
    this.inputNotes = document.getElementById("confirm-notes");
    this.btnSubmitBatch = document.getElementById("btn-submit-confirmed-batch");
    this.btnAskAiAboutItem = document.getElementById("btn-ask-ai-item");

    // State
    this.currentData = null;
    this.selectedDetectionIndex = 0;
    this.showBoundingBoxes = true;
    this.showLabels = true;
    this.confidenceThreshold = 0.25;

    this.categoryColors = {
      "Recyclable materials": "#2563eb",
      "Organic and biodegradable waste": "#16a34a",
      "Municipal solid waste": "#475569",
      "Hazardous waste": "#dc2626",
      "Electronic waste": "#d97706",
      "Liquid waste": "#7c3aed",
      "Construction and demolition waste": "#ca8a04",
      "Biomedical and healthcare waste": "#e11d48",
      "Plastic": "#2563eb",
      "Metal": "#2563eb",
      "Paper": "#2563eb",
      "Cardboard": "#2563eb",
      "Glass": "#2563eb"
    };

    this.init();
  }

  init() {
    this.initUploadEvents();
    this.initQuickSamples();
    this.initCameraEvents();
    this.initControls();
    this.initConfirmationEvents();
    this.initManualCategoryButtons();

    window.addEventListener("resize", () => {
      if (this.currentData && this.imgDisplay) {
        this.resizeOverlayCanvas();
        this.renderBoundingBoxes();
      }
    });
  }

  initUploadEvents() {
    if (!this.dropzone || !this.fileInput) return;

    this.dropzone.addEventListener("click", () => this.fileInput.click());

    this.dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      this.dropzone.classList.add("drag-over");
    });

    this.dropzone.addEventListener("dragleave", () => {
      this.dropzone.classList.remove("drag-over");
    });

    this.dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      this.dropzone.classList.remove("drag-over");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        this.handleFileUpload(e.dataTransfer.files[0]);
      }
    });

    this.fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        this.handleFileUpload(e.target.files[0]);
      }
    });
  }

  initQuickSamples() {
    document.querySelectorAll(".btn-sample-chip").forEach((chip) => {
      chip.addEventListener("click", (e) => {
        const sampleUrl = e.currentTarget.getAttribute("data-sample-url");
        if (sampleUrl) {
          this.inspectSampleImage(sampleUrl);
        }
      });
    });
  }

  initCameraEvents() {
    if (this.btnToggleCamera) {
      this.btnToggleCamera.addEventListener("click", () => this.startCamera());
    }
    if (this.btnStopCamera) {
      this.btnStopCamera.addEventListener("click", () => this.stopCamera());
    }
    if (this.btnCaptureCamera) {
      this.btnCaptureCamera.addEventListener("click", () => this.captureCameraFrame());
    }
    if (this.btnPauseCamera) {
      this.btnPauseCamera.addEventListener("click", () => this.togglePauseCamera());
    }
  }

  async startCamera() {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        if (window.showEcoSyncToast) window.showEcoSyncToast("Camera access is not supported on this browser.", "warning");
        return;
      }
      this.cameraStream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "environment" }
      });
      if (this.cameraVideo) {
        this.cameraVideo.srcObject = this.cameraStream;
        await this.cameraVideo.play();
      }
      if (this.cameraContainer) {
        this.cameraContainer.classList.add("active");
        this.cameraContainer.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      this.isCameraPaused = false;
      if (this.btnPauseCamera) this.btnPauseCamera.textContent = "Pause Feed";
      if (window.showEcoSyncToast) window.showEcoSyncToast("Camera stream started. Hold waste item in front of lens.");
    } catch (err) {
      console.error("Camera access error:", err);
      if (window.showEcoSyncToast) {
        window.showEcoSyncToast("Could not open camera: " + (err.message || "Permission denied"), "warning");
      }
    }
  }

  togglePauseCamera() {
    if (!this.cameraVideo || !this.cameraStream) return;
    if (this.isCameraPaused) {
      this.cameraVideo.play();
      this.isCameraPaused = false;
      if (this.btnPauseCamera) this.btnPauseCamera.textContent = "Pause Feed";
    } else {
      this.cameraVideo.pause();
      this.isCameraPaused = true;
      if (this.btnPauseCamera) this.btnPauseCamera.textContent = "Resume Feed";
    }
  }

  stopCamera() {
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach((track) => track.stop());
      this.cameraStream = null;
    }
    if (this.cameraContainer) {
      this.cameraContainer.classList.remove("active");
    }
    this.isCameraPaused = false;
  }

  captureCameraFrame() {
    if (!this.cameraVideo) return;
    const canvas = document.createElement("canvas");
    canvas.width = this.cameraVideo.videoWidth || 640;
    canvas.height = this.cameraVideo.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(this.cameraVideo, 0, 0);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `camera_frame_${Date.now()}.jpg`, { type: "image/jpeg" });
        this.stopCamera();
        this.handleFileUpload(file);
      }
    }, "image/jpeg", 0.92);
  }

  initControls() {
    if (this.confSlider) {
      this.confSlider.addEventListener("input", (e) => {
        this.confidenceThreshold = parseFloat(e.target.value);
        if (this.confValueText) {
          this.confValueText.textContent = `${Math.round(this.confidenceThreshold * 100)}%`;
        }
      });
      this.confSlider.addEventListener("change", () => {
        if (this.currentData && this.currentData.image) {
          this.reFilterOrReload();
        }
      });
    }

    if (this.toggleBoxes) {
      this.toggleBoxes.addEventListener("change", (e) => {
        this.showBoundingBoxes = e.target.checked;
        this.renderBoundingBoxes();
      });
    }

    if (this.toggleLabels) {
      this.toggleLabels.addEventListener("change", (e) => {
        this.showLabels = e.target.checked;
        this.renderBoundingBoxes();
      });
    }

    if (this.overlayCanvas) {
      this.overlayCanvas.addEventListener("click", (e) => this.onCanvasClick(e));
    }
  }

  initConfirmationEvents() {
    if (this.btnSubmitBatch) {
      this.btnSubmitBatch.addEventListener("click", async (e) => {
        e.preventDefault();
        await this.submitConfirmedBatch();
      });
    }

    if (this.btnAskAiAboutItem) {
      this.btnAskAiAboutItem.addEventListener("click", () => {
        const itemTitle = this.inputItemName ? this.inputItemName.value : "this waste item";
        if (window.aiAdvisor) {
          window.aiAdvisor.openWithPrompt(`How should my household handle, dispose of, or recycle ${itemTitle}?`);
        }
      });
    }
  }

  initManualCategoryButtons() {
    document.querySelectorAll(".btn-manual-cat").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const cat = e.currentTarget.getAttribute("data-cat");
        if (cat && this.selectCategory) {
          this.selectCategory.value = cat;
          this.renderManualCategoryGuidance(cat);
        }
      });
    });
  }

  async handleFileUpload(file) {
    if (!file) return;

    const allowed = ["image/jpeg", "image/png", "image/webp"];
    if (!allowed.includes(file.type)) {
      if (window.showEcoSyncToast) window.showEcoSyncToast("Please upload a JPEG, PNG, or WEBP image.", "warning");
      return;
    }
    if (file.size > 16 * 1024 * 1024) {
      if (window.showEcoSyncToast) window.showEcoSyncToast("File exceeds maximum allowed size of 16 MB.", "warning");
      return;
    }

    const formData = new FormData();
    formData.append("image", file);
    formData.append("confidence_threshold", this.confidenceThreshold);

    this.setLoadingState(true);

    try {
      const resp = await fetch("/api/detect", {
        method: "POST",
        body: formData
      });
      const data = await resp.json();
      this.setLoadingState(false);

      if (data.status === "success") {
        this.displayResults(data.data);
      } else {
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast("Detection error: " + (data.message || "Failed to process image"), "warning");
        }
      }
    } catch (err) {
      this.setLoadingState(false);
      console.error("Network error during detection:", err);
      if (window.showEcoSyncToast) {
        window.showEcoSyncToast("Could not reach computer vision service.", "warning");
      }
    }
  }

  async inspectSampleImage(samplePath) {
    this.setLoadingState(true);
    try {
      const resp = await fetch("/api/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sample_path: samplePath,
          confidence_threshold: this.confidenceThreshold
        })
      });
      const data = await resp.json();
      this.setLoadingState(false);

      if (data.status === "success") {
        this.displayResults(data.data);
      } else {
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast("Sample inspection error: " + (data.message || "Failed to process sample"), "warning");
        }
      }
    } catch (err) {
      this.setLoadingState(false);
      console.error("Error inspecting sample:", err);
      if (window.showEcoSyncToast) {
        window.showEcoSyncToast("Failed to inspect sample image.", "warning");
      }
    }
  }

  setLoadingState(isLoading) {
    const dropTitle = document.querySelector(".dropzone-title");
    if (dropTitle) {
      dropTitle.textContent = isLoading ? "RUNNING YOLO11n INFERENCE..." : "UPLOAD OR DRAG WASTE PHOTO";
    }
    if (this.dropzone) {
      this.dropzone.style.opacity = isLoading ? "0.6" : "1";
    }
  }

  displayResults(resultData) {
    this.currentData = resultData;
    this.selectedDetectionIndex = 0;

    if (this.stageContainer) {
      this.stageContainer.style.display = "block";
    }

    if (this.imgDisplay) {
      this.imgDisplay.src = resultData.image.url;
      this.imgDisplay.onload = () => {
        this.resizeOverlayCanvas();
        this.renderBoundingBoxes();
      };
      if (this.imgDisplay.complete && this.imgDisplay.naturalWidth > 0) {
        this.resizeOverlayCanvas();
        this.renderBoundingBoxes();
      }
    }

    // Title and uncertainty note
    if (this.countTitle) {
      if (resultData.count === 0) {
        this.countTitle.textContent = "UNFAMILIAR ITEM / LOW CONFIDENCE";
      } else {
        this.countTitle.textContent = `${resultData.count} OBJECT${resultData.count === 1 ? "" : "S"} IDENTIFIED`;
      }
    }

    // Category badges
    if (this.categoryBadgesWrap) {
      this.categoryBadgesWrap.innerHTML = "";
      Object.entries(resultData.category_summary || {}).forEach(([cat, count]) => {
        const badge = document.createElement("span");
        badge.className = "badge-tag";
        badge.style.cssText = "font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 9999px; background: #e2e8f0; color: #334155;";
        badge.textContent = `${count} ${cat}`;
        this.categoryBadgesWrap.appendChild(badge);
      });
    }

    // Render detections list
    this.renderDetectionsList();

    // Show guidance for first detection or manual fallback
    if (resultData.detections && resultData.detections.length > 0) {
      this.updateGuidanceDisplay(resultData.detections[0]);
    } else {
      this.showUncertaintyFallback(resultData.uncertainty_note);
    }
  }

  renderDetectionsList() {
    if (!this.detectionsList || !this.currentData) return;
    this.detectionsList.innerHTML = "";

    const detections = this.currentData.detections || [];
    if (detections.length === 0) {
      this.detectionsList.innerHTML = `
        <div style="padding: 16px; background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; font-size: 13px; color: #92400e;">
          <p><strong>Honest AI Notice:</strong> No standard household items were detected above ${Math.round(this.confidenceThreshold * 100)}% confidence.</p>
          <p style="font-size: 12px; margin-top: 4px;">EcoSync avoids guessing or fabricating classifications. Please choose the correct waste category below.</p>
        </div>
      `;
      return;
    }

    detections.forEach((det, idx) => {
      const item = document.createElement("div");
      item.className = `detection-row-item ${this.selectedDetectionIndex === idx ? "selected" : ""}`;
      item.innerHTML = `
        <div class="detection-row-left">
          <span class="detection-idx">#${det.index}</span>
          <div>
            <div class="detection-name">${det.object_identity || det.candidate_material}</div>
            <div class="detection-sub">Model detected: <code>${det.raw_class}</code> • Suggested: <strong>${det.suggested_category}</strong></div>
          </div>
        </div>
        <div class="detection-conf-badge">${det.confidence_pct}% CONF</div>
      `;

      item.addEventListener("click", () => {
        this.selectedDetectionIndex = idx;
        this.renderDetectionsList();
        this.renderBoundingBoxes();
        this.updateGuidanceDisplay(det);
      });

      this.detectionsList.appendChild(item);
    });
  }

  updateGuidanceDisplay(det) {
    if (!det) return;

    const g = det.how_to_handle || {};
    const catInfo = det.category_info || {};

    // Update primary bin callout banner
    const banner = document.getElementById("scanner-target-bin-banner");
    const binIcon = document.getElementById("scanner-bin-icon");
    const binTitle = document.getElementById("scanner-bin-title");
    const binSub = document.getElementById("scanner-bin-sub");

    if (banner && binTitle) {
      const cat = det.suggested_category || "Recyclable materials";
      let bannerClass = "blue";
      let icon = "🔵";
      let title = "BLUE BIN — RECYCLABLES";
      let subtitle = "Clean dry paper, cardboard, plastic bottles & cans";

      if (cat.includes("Organic")) {
        bannerClass = "green";
        icon = "🟢";
        title = "GREEN BIN — WET COMPOST & ORGANICS";
        subtitle = "Kitchen food scraps, fruit rinds, vegetable peels, coffee grounds";
      } else if (cat.includes("Electronic")) {
        bannerClass = "amber";
        icon = "🟠";
        title = "ORANGE KIOSK — CERTIFIED E-WASTE ONLY";
        subtitle = "Mobile phones, chargers, circuit boards, small home appliances";
      } else if (cat.includes("Hazardous")) {
        bannerClass = "red";
        icon = "🔴";
        title = "HAZARDOUS DEPOT — DO NOT CURBSIDE BIN";
        subtitle = "Batteries, CFL bulbs, paint residues, toxic chemicals";
      } else if (cat.includes("Liquid")) {
        bannerClass = "red";
        icon = "🛢️";
        title = "SEALED BOTTLE DEPOT — NEVER DOWN DRAINS";
        subtitle = "Cooled used cooking oils and motor lubricants";
      } else if (cat.includes("Municipal solid")) {
        bannerClass = "charcoal";
        icon = "🗑️";
        title = "GRAY/BLACK BIN — GENERAL TRASH";
        subtitle = "Non-recyclable mixed wrappers, multi-material plastics";
      }

      banner.className = `target-bin-banner ${bannerClass}`;
      if (binIcon) binIcon.textContent = icon;
      binTitle.textContent = title;
      if (binSub) binSub.textContent = subtitle;
    }

    // Update 8-point guidance UI
    const elWhat = document.getElementById("guide-p-what");
    const elNow = document.getElementById("guide-p-now");
    const elBin = document.getElementById("guide-p-bin");
    const elPrep = document.getElementById("guide-p-prep");
    const elAvoid = document.getElementById("guide-p-avoid");
    const elWhere = document.getElementById("guide-p-where");
    const elWhy = document.getElementById("guide-p-why");
    const elAction = document.getElementById("guide-p-action");
    const safetyBox = document.getElementById("scanner-safety-alert");

    if (elWhat) elWhat.textContent = g.what_is_it || det.object_identity;
    if (elNow) elNow.textContent = g.what_to_do_now || "Inspect cleanliness and prepare for proper waste stream.";
    if (elBin) elBin.textContent = g.which_bin || `${catInfo.bin_color || 'Standard'} (${catInfo.bin_label || ''})`;
    if (elPrep) elPrep.textContent = g.how_to_prepare || "Empty and clean off residual food or liquids.";
    if (elAvoid) elAvoid.textContent = g.what_to_avoid || "Avoid mixing with incompatible waste streams.";
    if (elWhere) elWhere.textContent = g.where_should_it_go || "Follow municipal collection schedule or local drop-off center.";
    if (elWhy) elWhy.textContent = g.why_matters || "Proper sorting keeps valuable materials in circulation and reduces landfill methane.";
    if (elAction) elAction.textContent = g.citizen_action || "Carry reusables whenever possible to reduce disposable items.";

    // Safety Alert
    if (safetyBox) {
      if (det.safety_warning) {
        safetyBox.textContent = `⚠️ Safety Notice: ${det.safety_warning}`;
        safetyBox.style.display = "block";
      } else {
        safetyBox.style.display = "none";
      }
    }

    // Pre-populate confirmation form
    if (this.selectCategory) this.selectCategory.value = det.suggested_category || "Recyclable materials";
    if (this.inputItemName) this.inputItemName.value = det.object_identity || det.raw_class;
    if (this.inputWeight) this.inputWeight.value = det.estimated_weight_kg || 0.05;

    // Show guidance card
    if (this.guidanceCard) this.guidanceCard.style.display = "block";
  }

  showUncertaintyFallback(note) {
    if (this.guidanceCard) this.guidanceCard.style.display = "block";
    const elWhat = document.getElementById("guide-p-what");
    if (elWhat) elWhat.textContent = note || "Uncertain item. Please pick a category manually.";
  }

  renderManualCategoryGuidance(catName) {
    if (this.selectCategory) this.selectCategory.value = catName;
    if (this.inputItemName) this.inputItemName.value = `Household Item (${catName})`;
    if (this.guidanceCard) this.guidanceCard.style.display = "block";
  }

  resizeOverlayCanvas() {
    if (!this.imgDisplay || !this.overlayCanvas) return;
    const rect = this.imgDisplay.getBoundingClientRect();
    this.overlayCanvas.width = rect.width;
    this.overlayCanvas.height = rect.height;
  }

  renderBoundingBoxes() {
    if (!this.ctx || !this.overlayCanvas || !this.currentData || !this.imgDisplay) return;

    const w = this.overlayCanvas.width;
    const h = this.overlayCanvas.height;
    this.ctx.clearRect(0, 0, w, h);

    if (!this.showBoundingBoxes) return;

    const detections = this.currentData.detections || [];
    detections.forEach((det, idx) => {
      const norm = det.bounding_box.normalized;
      const bx = norm.x1 * w;
      const by = norm.y1 * h;
      const bw = norm.width * w;
      const bh = norm.height * h;

      const isSelected = this.selectedDetectionIndex === idx;
      const strokeColor = isSelected ? "#10b981" : "#3b82f6";

      // Draw box
      this.ctx.save();
      this.ctx.strokeStyle = strokeColor;
      this.ctx.lineWidth = isSelected ? 3 : 2;
      this.ctx.strokeRect(bx, by, bw, bh);

      // Subtle fill for selected box
      if (isSelected) {
        this.ctx.fillStyle = "rgba(16, 185, 129, 0.15)";
        this.ctx.fillRect(bx, by, bw, bh);
      }

      // Draw label
      if (this.showLabels) {
        const labelText = `#${det.index} ${det.object_identity} (${det.confidence_pct}%)`;
        this.ctx.font = "bold 11px system-ui, sans-serif";
        const textMetrics = this.ctx.measureText(labelText);
        const bgW = textMetrics.width + 10;
        const bgH = 18;

        this.ctx.fillStyle = strokeColor;
        this.ctx.fillRect(bx, Math.max(0, by - bgH), bgW, bgH);

        this.ctx.fillStyle = "#ffffff";
        this.ctx.fillText(labelText, bx + 5, Math.max(12, by - 4));
      }

      this.ctx.restore();
    });
  }

  onCanvasClick(e) {
    if (!this.currentData || !this.overlayCanvas) return;
    const rect = this.overlayCanvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;
    const w = this.overlayCanvas.width;
    const h = this.overlayCanvas.height;

    let foundIdx = null;
    (this.currentData.detections || []).forEach((det, idx) => {
      const norm = det.bounding_box.normalized;
      const bx = norm.x1 * w;
      const by = norm.y1 * h;
      const bw = norm.width * w;
      const bh = norm.height * h;

      if (clickX >= bx && clickX <= bx + bw && clickY >= by && clickY <= by + bh) {
        foundIdx = idx;
      }
    });

    if (foundIdx !== null) {
      this.selectedDetectionIndex = foundIdx;
      this.renderDetectionsList();
      this.renderBoundingBoxes();
      this.updateGuidanceDisplay(this.currentData.detections[foundIdx]);
    }
  }

  async submitConfirmedBatch() {
    const itemName = this.inputItemName ? this.inputItemName.value.trim() : "Household Item";
    const category = this.selectCategory ? this.selectCategory.value : "Recyclable materials";
    const action = this.selectAction ? this.selectAction.value : "Confirmed & Segregated";
    const weight = parseFloat(this.inputWeight ? this.inputWeight.value : 0.05);
    const notes = this.inputNotes ? this.inputNotes.value.trim() : "";

    const payload = {
      detection_batch_id: this.currentData ? this.currentData.detection_batch_id : null,
      confirmed_category: category,
      item_name: itemName,
      action_taken: action,
      estimated_weight_kg: weight,
      sub_type: itemName,
      notes: notes || `Household action: ${action}`
    };

    try {
      const resp = await fetch("/api/classifications/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();

      if (data.status === "success") {
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast(`Confirmed "${itemName}" sorted into ${category}! (+${weight} kg logged)`);
        }
        if (window.householdImpact) {
          window.householdImpact.fetchImpactMetrics();
          window.householdImpact.fetchHistory();
        }
        if (window.ecosyncApp) window.ecosyncApp.fetchHomeLiveStats();
        if (window.digitalTwin) window.digitalTwin.fetchTopology();
      } else {
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast("Confirmation error: " + data.message, "warning");
        }
      }
    } catch (err) {
      console.error("Confirmation error:", err);
      if (window.showEcoSyncToast) {
        window.showEcoSyncToast("Failed to record household scan action.", "warning");
      }
    }
  }
}

window.WasteScanner = WasteScanner;
