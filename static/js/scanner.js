/**
 * ECOSYNC — AI Vision Studio Scanner Controller
 * Matches Reference Image 4.
 * Real YOLOv8 inference, aligned SVG bounding boxes, 17-class mapping, and instant disposal confirmation.
 */

class WasteScanner {
  constructor() {
    this.dropzone = document.getElementById("scanner-dropzone");
    this.fileInput = document.getElementById("scanner-file-input");
    this.uploadArea = document.getElementById("scanner-upload-area");
    this.cameraArea = document.getElementById("scanner-camera-area");
    this.videoEl = document.getElementById("scanner-video-preview");

    this.tabUpload = document.getElementById("tab-btn-upload");
    this.tabCamera = document.getElementById("tab-btn-camera");

    this.btnCapture = document.getElementById("btn-camera-capture");
    this.btnStopCam = document.getElementById("btn-camera-stop");

    this.sliderConf = document.getElementById("range-conf-threshold");
    this.valConfText = document.getElementById("val-conf-threshold");

    this.awaitingState = document.getElementById("scanner-awaiting-state");
    this.activeOutput = document.getElementById("scanner-active-output");
    this.renderedImg = document.getElementById("scan-rendered-img");
    this.renderedSvg = document.getElementById("scan-rendered-svg");
    this.detectionsList = document.getElementById("scanner-detections-list");

    this.currentData = null;
    this.cameraStream = null;
    this.virtualCamTimer = null;
    this.isStartingCamera = false;
    this.confThreshold = 0.20;

    this.init();
  }

  init() {
    this.initUpload();
    this.initSlider();
  }

  setSourceMode(mode) {
    if (mode === "upload") {
      if (this.tabUpload) this.tabUpload.classList.add("active");
      if (this.tabCamera) this.tabCamera.classList.remove("active");
      if (this.uploadArea) this.uploadArea.style.display = "block";
      if (this.cameraArea) this.cameraArea.style.display = "none";
      this.stopCamera();
    } else {
      if (this.tabUpload) this.tabUpload.classList.remove("active");
      if (this.tabCamera) this.tabCamera.classList.add("active");
      if (this.uploadArea) this.uploadArea.style.display = "none";
      if (this.cameraArea) this.cameraArea.style.display = "block";
      this.startCamera();
    }
  }

  initUpload() {
    if (this.dropzone && this.fileInput) {
      this.dropzone.addEventListener("click", () => this.fileInput.click());

      this.dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        this.dropzone.classList.add("dragover");
      });

      this.dropzone.addEventListener("dragleave", () => {
        this.dropzone.classList.remove("dragover");
      });

      this.dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        this.dropzone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          this.uploadFile(e.dataTransfer.files[0]);
        }
      });

      this.fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files.length > 0) {
          this.uploadFile(e.target.files[0]);
        }
      });
    }
  }

  initSlider() {
    if (this.sliderConf) {
      this.sliderConf.addEventListener("input", (e) => {
        this.confThreshold = parseFloat(e.target.value);
        if (this.valConfText) {
          this.valConfText.textContent = `${Math.round(this.confThreshold * 100)}%`;
        }
      });
    }
  }

  async startCamera() {
    if (this.isStartingCamera) return;
    this.isStartingCamera = true;

    // Show camera area immediately
    if (this.uploadArea) this.uploadArea.style.display = "none";
    if (this.cameraArea) this.cameraArea.style.display = "block";
    if (this.tabUpload) this.tabUpload.classList.remove("active");
    if (this.tabCamera) this.tabCamera.classList.add("active");

    const statusOverlay = document.getElementById("scanner-cam-status-overlay");
    const statusText = document.getElementById("scanner-cam-status-text");
    const statusActions = document.getElementById("scanner-cam-status-actions");

    if (statusOverlay) {
      statusOverlay.style.display = "flex";
      if (statusText) statusText.innerHTML = `
        <div class="welcome-spinner-ring" style="width:32px; height:32px; margin:0 auto 12px;"></div>
        <div style="font-family:var(--font-mono); font-size:13px; color:var(--brand-neon);">
          CONNECTING TO WEBCAM HARDWARE...
        </div>
        <div style="font-size:12px; color:var(--text-secondary); margin-top:6px;">
          Please select "Allow" if prompted for camera permission.
        </div>
      `;
      if (statusActions) statusActions.style.display = "none";
    }

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("WebRTC camera API is not supported in this browser context.");
      }

      // Stop any existing stream first
      if (this.cameraStream) {
        try {
          this.cameraStream.getTracks().forEach(t => t.stop());
        } catch (e) {}
        this.cameraStream = null;
      }
      if (this.virtualCamTimer) {
        clearInterval(this.virtualCamTimer);
        this.virtualCamTimer = null;
      }

      // Attempt standard universal video constraint first
      let stream = null;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false
        });
      } catch (err1) {
        console.warn("Direct video:true request failed, attempting resolution constraints:", err1);
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false
        });
      }

      this.cameraStream = stream;

      if (this.videoEl) {
        this.videoEl.srcObject = this.cameraStream;
        this.videoEl.muted = true;
        this.videoEl.playsInline = true;
        this.videoEl.setAttribute("playsinline", "true");
        this.videoEl.setAttribute("muted", "true");

        // Wait for metadata ready before play
        await new Promise((resolve) => {
          const timeout = setTimeout(() => resolve(), 2000);
          this.videoEl.onloadedmetadata = () => {
            clearTimeout(timeout);
            this.videoEl.play().then(resolve).catch(resolve);
          };
        });

        try {
          await this.videoEl.play();
        } catch (playErr) {
          console.warn("Autoplay notice:", playErr);
        }
      }

      if (statusOverlay) {
        statusOverlay.style.display = "none";
      }

      if (window.showEcoSyncToast) {
        window.showEcoSyncToast("Live webcam connected! Point at an item and click 'Snap & Detect'.");
      }

    } catch (err) {
      console.error("Camera access failed:", err);
      if (statusOverlay) {
        statusOverlay.style.display = "flex";
        let reason = "Could Not Connect to Webcam";
        let advice = "Please verify browser permissions and try again.";

        if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
          reason = "Camera Permission Blocked";
          advice = "Click the camera or lock icon in your browser URL bar, set Camera to 'Allow', then click Retry.";
        } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
          reason = "No Webcam Hardware Detected";
          advice = "No physical webcam was found on this device. You can test the scanner workflow with a Virtual Stream or upload a file.";
        } else if (err.name === "NotReadableError" || err.name === "TrackStartError") {
          reason = "Webcam in Use by Another Application";
          advice = "Another app (Zoom, Teams, or another tab) is currently using the camera. Close it and click Retry.";
        }

        if (statusText) {
          statusText.innerHTML = `
            <div style="font-size:26px; margin-bottom:8px;">📷⚠️</div>
            <div style="font-family:var(--font-mono); font-size:14px; font-weight:700; color:#f87171; margin-bottom:6px;">
              ${reason}
            </div>
            <div style="font-size:12.5px; color:var(--text-secondary); max-width:380px; line-height:1.5;">
              ${advice}
            </div>
          `;
        }
        if (statusActions) {
          statusActions.style.display = "flex";
        }
      }
    } finally {
      this.isStartingCamera = false;
    }
  }

  startVirtualCamera() {
    const statusOverlay = document.getElementById("scanner-cam-status-overlay");
    if (statusOverlay) statusOverlay.style.display = "none";

    // Create a live simulated camera canvas stream
    const canvas = document.createElement("canvas");
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext("2d");

    const sampleImages = [
      "/static/images/samples/sample_redbull.jpg",
      "/static/images/samples/sample_bottle.jpg",
      "/static/images/samples/sample_apple.jpg"
    ];
    let sampleIdx = 0;
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = sampleImages[sampleIdx];

    if (this.virtualCamTimer) clearInterval(this.virtualCamTimer);
    let frameCount = 0;

    this.virtualCamTimer = setInterval(() => {
      frameCount++;
      // Switch image every ~120 frames
      if (frameCount % 120 === 0) {
        sampleIdx = (sampleIdx + 1) % sampleImages.length;
        img.src = sampleImages[sampleIdx];
      }

      ctx.fillStyle = "#060f09";
      ctx.fillRect(0, 0, 640, 480);

      if (img.complete && img.naturalWidth > 0) {
        ctx.drawImage(img, 20, 20, 600, 440);
      }

      // Live HUD watermark
      ctx.fillStyle = "rgba(4, 8, 6, 0.75)";
      ctx.fillRect(14, 14, 250, 28);
      ctx.fillStyle = "#00e599";
      ctx.font = "11px 'Space Mono', monospace";
      ctx.fillText(`● VIRTUAL CAM // ${new Date().toLocaleTimeString()}`, 24, 32);
    }, 40);

    const stream = canvas.captureStream(30);
    this.cameraStream = stream;

    if (this.videoEl) {
      this.videoEl.srcObject = stream;
      this.videoEl.muted = true;
      this.videoEl.playsInline = true;
      this.videoEl.play().catch(e => console.warn(e));
    }

    if (window.showEcoSyncToast) {
      window.showEcoSyncToast("Virtual camera stream active! Click 'Snap & Detect Frame' to test.");
    }
  }

  stopCamera() {
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach(track => {
        try { track.stop(); } catch(e) {}
      });
      this.cameraStream = null;
    }
    if (this.virtualCamTimer) {
      clearInterval(this.virtualCamTimer);
      this.virtualCamTimer = null;
    }
    if (this.videoEl) {
      this.videoEl.pause();
      this.videoEl.srcObject = null;
    }
    const statusOverlay = document.getElementById("scanner-cam-status-overlay");
    if (statusOverlay) statusOverlay.style.display = "none";

    if (this.cameraArea) this.cameraArea.style.display = "none";
    if (this.uploadArea) this.uploadArea.style.display = "block";
    if (this.tabUpload) this.tabUpload.classList.add("active");
    if (this.tabCamera) this.tabCamera.classList.remove("active");
    if (window.showEcoSyncToast) {
      window.showEcoSyncToast("Camera stopped. Switched back to File Upload.");
    }
  }

  captureFrame() {
    if (!this.videoEl || !this.cameraStream) {
      if (window.showEcoSyncToast) window.showEcoSyncToast("Camera stream is not active. Starting camera...", "warning");
      this.startCamera();
      return;
    }

    const flash = document.getElementById("scanner-cam-flash");
    if (flash) {
      flash.style.opacity = "0.85";
      setTimeout(() => { flash.style.opacity = "0"; }, 120);
    }

    const vw = this.videoEl.videoWidth || this.videoEl.clientWidth || 640;
    const vh = this.videoEl.videoHeight || this.videoEl.clientHeight || 480;

    const canvas = document.createElement("canvas");
    canvas.width = vw;
    canvas.height = vh;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(this.videoEl, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL("image/jpeg", 0.90);
    if (window.showEcoSyncToast) {
      window.showEcoSyncToast("📸 Frame captured! Analyzing waste item...");
    }
    this.sendImagePayload({ image_base64: dataUrl });
  }

  async uploadFile(file) {
    const formData = new FormData();
    formData.append("image", file);
    formData.append("confidence_threshold", this.confThreshold);

    this.showScanningState();

    try {
      const resp = await fetch("/api/detect", {
        method: "POST",
        body: formData
      });
      const data = await resp.json();
      if (data.status === "success") {
        this.displayResults(data.data);
      } else {
        alert(data.message || "Detection error.");
      }
    } catch (err) {
      console.error("Upload error:", err);
    }
  }

  async loadSample(samplePath) {
    this.showScanningState();
    try {
      const resp = await fetch("/api/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sample_path: samplePath,
          confidence_threshold: this.confThreshold
        })
      });
      const data = await resp.json();
      if (data.status === "success") {
        this.displayResults(data.data);
      }
    } catch (err) {
      console.error("Sample detect error:", err);
    }
  }

  async sendImagePayload(payload) {
    this.showScanningState();
    payload.confidence_threshold = this.confThreshold;

    try {
      const resp = await fetch("/api/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (data.status === "success") {
        this.displayResults(data.data);
      }
    } catch (err) {
      console.error("Inference payload error:", err);
    }
  }

  showScanningState() {
    if (this.awaitingState) this.awaitingState.style.display = "none";
    if (this.activeOutput) {
      this.activeOutput.style.display = "block";
      this.detectionsList.innerHTML = `
        <div style="text-align:center; padding:30px; font-family:var(--font-mono); color:var(--brand-neon);">
          ⚡ RUNNING YOLOV8 NEURAL INFERENCE...
        </div>
      `;
    }
  }

  displayResults(data) {
    this.currentData = data;
    if (this.awaitingState) this.awaitingState.style.display = "none";
    if (this.activeOutput) this.activeOutput.style.display = "block";

    const imgUrl = (data.image && data.image.url) ? data.image.url : (data.image_filename ? `/uploads/${data.image_filename}` : "");
    if (this.renderedImg) {
      this.renderedImg.src = imgUrl;
      this.renderedImg.onload = () => {
        this.renderSvgBoundingBoxes(data);
      };
    }

    this.renderDetectionsList(data);
  }

  renderSvgBoundingBoxes(data) {
    if (!this.renderedSvg || !data.detections || data.detections.length === 0) {
      if (this.renderedSvg) this.renderedSvg.innerHTML = "";
      return;
    }

    const imgW = (data.image && data.image.width) ? data.image.width : (data.image_dimensions ? data.image_dimensions.width : 800);
    const imgH = (data.image && data.image.height) ? data.image.height : (data.image_dimensions ? data.image_dimensions.height : 600);

    this.renderedSvg.setAttribute("viewBox", `0 0 ${imgW} ${imgH}`);
    let svgContent = "";

    data.detections.forEach((det) => {
      const b = det.bounding_box.pixel;
      const x = b.x1;
      const y = b.y1;
      const w = b.width;
      const h = b.height;
      const isWaste = det.is_waste !== false && det.suggested_category !== "Uncategorized";
      const color = isWaste ? (det.bin_color || "#00e599") : "#a855f7";

      const label = isWaste ? `${det.object_identity} (${det.confidence_pct}%)` : `👤 ${det.object_identity} (Uncategorized)`;
      const labelW = Math.min(w, label.length * 9 + 20);

      svgContent += `
        <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${isWaste ? 'rgba(0, 229, 153, 0.08)' : 'rgba(168, 85, 247, 0.08)'}" stroke="${color}" stroke-width="3" rx="6" style="filter:drop-shadow(0 0 8px ${color});"/>
        <rect x="${x}" y="${Math.max(0, y - 26)}" width="${labelW}" height="24" fill="${color}" rx="4"/>
        <text x="${x + 6}" y="${Math.max(0, y - 26) + 16}" fill="#060c09" font-family="'Space Mono', monospace" font-size="12" font-weight="700">
          ${label}
        </text>
      `;
    });

    this.renderedSvg.innerHTML = svgContent;
  }

  renderDetectionsList(data) {
    if (!this.detectionsList) return;
    this.detectionsList.innerHTML = "";

    const dets = data.detections || [];
    if (dets.length === 0) {
      this.detectionsList.innerHTML = `
        <div class="detection-identity-card" style="text-align:center;">
          <h4 style="color:var(--text-muted);">No distinct waste items detected at current threshold.</h4>
          <p style="font-size:13px; color:var(--text-secondary); margin-top:8px;">Try lowering sensitivity slider or uploading a clearer, well-lit photo.</p>
        </div>
      `;
      return;
    }

    dets.forEach((det, idx) => {
      const card = document.createElement("div");
      card.className = "detection-identity-card";
      const isWaste = det.is_waste !== false && det.suggested_category !== "Uncategorized";
      const prep = (det.how_to_handle && det.how_to_handle.how_to_prepare) ? det.how_to_handle.how_to_prepare : (det.how_to_handle ? det.how_to_handle.what_to_do_now : "");

      const badgeStyle = !isWaste ? 'background:rgba(168,85,247,0.18); border:1px solid #a855f7; color:#c084fc;' : '';
      const destStyle = !isWaste ? 'border:1px solid #a855f7; color:#c084fc; background:rgba(168,85,247,0.08);' : '';

      let actionBtnHtml = "";
      if (isWaste) {
        actionBtnHtml = `
          <button class="det-confirm-btn" id="btn-confirm-det-${idx}">
            ✓ Confirm & Record in Digital Twin
          </button>
        `;
      } else {
        actionBtnHtml = `
          <button class="det-confirm-btn" disabled style="background:#2e1065; color:#c084fc; border:1px solid #a855f7; cursor:not-allowed; opacity:0.9; font-size:13px;">
            👤 Citizen Detected (Uncategorized Non-Waste)
          </button>
        `;
      }

      card.innerHTML = `
        <div class="det-header-row">
          <span class="det-title">${!isWaste ? '👤 ' : ''}${det.object_identity}</span>
          <span class="det-conf-badge" style="${badgeStyle}">${!isWaste ? 'Non-Waste // ' : ''}${det.confidence_pct}% Confidence</span>
        </div>
        <div class="det-material-tag">
          <strong>Entity:</strong> ${det.candidate_material}
        </div>
        <div class="det-bin-route-box" style="${destStyle}">
          <strong>Classification:</strong> ${det.bin_target || det.suggested_category}
        </div>
        <p class="det-guidance-text">
          <strong>Guidance:</strong> ${prep}
        </p>
        ${actionBtnHtml}
      `;

      if (isWaste) {
        const btn = card.querySelector(`#btn-confirm-det-${idx}`);
        if (btn) {
          btn.addEventListener("click", () => this.confirmScan(det, data.detection_id, btn));
        }
      }

      this.detectionsList.appendChild(card);
    });
  }

  async confirmScan(det, batchId, btnEl) {
    if (det.is_waste === false || det.suggested_category === "Uncategorized" || det.raw_class === "person") {
      if (window.showEcoSyncToast) {
        window.showEcoSyncToast("Non-waste entity (Person) cannot be logged as waste.", "warning");
      }
      return;
    }

    btnEl.disabled = true;
    btnEl.textContent = "Recording...";

    try {
      const resp = await fetch("/api/household/scans", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          detection_id: batchId,
          image_url: this.currentData.image ? this.currentData.image.url : "",
          item_name: det.object_identity,
          category: det.suggested_category,
          material: det.candidate_material,
          confidence: det.confidence,
          action_taken: `Sorted into ${det.bin_target || det.suggested_category}`,
          estimated_weight_kg: det.estimated_weight_kg || 0.05,
          user_notes: `Confirmed via EcoSync Vision Studio: ${det.raw_class}`
        })
      });

      const res = await resp.json();
      if (res.status === "success") {
        btnEl.textContent = "✓ Recorded in Database";
        btnEl.style.backgroundColor = "#166534";
        btnEl.style.color = "#ffffff";
        btnEl.style.borderColor = "#22c55e";
        if (window.showEcoSyncToast) {
          window.showEcoSyncToast(`✓ Recorded: ${det.object_identity} saved to database!`);
        }
        if (window.householdImpact) {
          window.householdImpact.fetchImpactMetrics();
          window.householdImpact.fetchHistory();
        }
        if (window.ecosyncApp) {
          window.ecosyncApp.fetchHomeLiveStats();
        }
      } else {
        btnEl.disabled = false;
        btnEl.textContent = "Retry Recording";
        alert(res.message || "Could not record scan.");
      }
    } catch (err) {
      console.error("Error confirming scan:", err);
      btnEl.disabled = false;
      btnEl.textContent = "Retry Recording";
    }
  }
}

if (!window.wasteScanner) {
  window.wasteScanner = new WasteScanner();
}
window.ecosyncScanner = window.wasteScanner;
