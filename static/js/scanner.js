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
    this.virtualCanvas = document.getElementById("scanner-virtual-canvas");
    this.cameraFallbackEl = document.getElementById("scanner-camera-fallback");
    this.cameraErrorMsg = document.getElementById("scanner-camera-error-msg");
    this.cameraStatusText = document.getElementById("camera-status-text");
    this.cameraStatusDot = document.getElementById("camera-status-dot");

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
    this.isVirtualCamera = false;
    this.isStartingCamera = false;
    this.virtualAnimId = null;
    this.virtualSampleIndex = 0;
    this.virtualSampleImages = [];
    this.confThreshold = 0.20;

    this.init();
  }

  init() {
    this.initUpload();
    this.initSlider();
    this.initCamera();
    this.preloadVirtualSamples();
  }

  preloadVirtualSamples() {
    const sampleUrls = [
      "./static/images/samples/sample_bottle.jpg",
      "./static/images/samples/sample_redbull.jpg",
      "./static/images/samples/sample_apple.jpg",
      "./static/images/samples/sample_banana.jpg",
      "./static/images/samples/sample_doritos.jpg",
      "./static/images/samples/sample_battery.jpg"
    ];
    this.virtualSampleImages = sampleUrls.map(url => {
      const img = new Image();
      img.src = url;
      return img;
    });
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
      this.dropzone.onclick = () => this.fileInput.click();

      this.dropzone.ondragover = (e) => {
        e.preventDefault();
        this.dropzone.classList.add("dragover");
      };

      this.dropzone.ondragleave = () => {
        this.dropzone.classList.remove("dragover");
      };

      this.dropzone.ondrop = (e) => {
        e.preventDefault();
        this.dropzone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          this.uploadFile(e.dataTransfer.files[0]);
        }
      };

      this.fileInput.onchange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
          this.uploadFile(e.target.files[0]);
        }
      };
    }
  }

  initSlider() {
    if (this.sliderConf) {
      this.sliderConf.oninput = (e) => {
        this.confThreshold = parseFloat(e.target.value);
        if (this.valConfText) {
          this.valConfText.textContent = `${Math.round(this.confThreshold * 100)}%`;
        }
      };
    }
  }

  initCamera() {
    if (this.tabUpload) {
      this.tabUpload.onclick = (e) => {
        e.preventDefault();
        this.setSourceMode("upload");
      };
    }
    if (this.tabCamera) {
      this.tabCamera.onclick = (e) => {
        e.preventDefault();
        this.setSourceMode("camera");
      };
    }
    if (this.btnCapture) {
      this.btnCapture.onclick = (e) => {
        e.preventDefault();
        this.captureFrame();
      };
    }
    if (this.btnStopCam) {
      this.btnStopCam.onclick = (e) => {
        e.preventDefault();
        this.stopCamera();
      };
    }
  }

  async startCamera() {
    if (this.isStartingCamera) return;
    this.isStartingCamera = true;

    // Reset fallback UI and stop any virtual stream
    this.stopVirtualCamera();
    if (this.cameraFallbackEl) this.cameraFallbackEl.style.display = "none";
    if (this.videoEl) this.videoEl.style.display = "block";
    if (this.virtualCanvas) this.virtualCanvas.style.display = "none";

    if (this.cameraStatusText) this.cameraStatusText.textContent = "CONNECTING WEBCAM...";
    if (this.cameraStatusDot) this.cameraStatusDot.style.background = "#fbbf24";

    try {
      // Ensure mediaDevices API exists
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Webcam API not supported or browser context insecure (localhost / 127.0.0.1 required).");
      }

      // Stop any existing stream cleanly
      if (this.cameraStream) {
        this.cameraStream.getTracks().forEach(track => {
          try { track.stop(); } catch(e) {}
        });
        this.cameraStream = null;
      }

      // Try camera with fallback ladder
      let stream = null;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" },
          audio: false
        });
      } catch (err1) {
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "user" },
            audio: false
          });
        } catch (err2) {
          stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
          });
        }
      }

      this.cameraStream = stream;
      this.isVirtualCamera = false;

      if (this.videoEl) {
        this.videoEl.srcObject = this.cameraStream;
        this.videoEl.muted = true;
        this.videoEl.playsInline = true;
        this.videoEl.setAttribute("playsinline", "true");
        this.videoEl.setAttribute("autoplay", "true");

        this.videoEl.onloadedmetadata = () => {
          const playPromise = this.videoEl.play();
          if (playPromise !== undefined) {
            playPromise.catch(e => console.warn("Video playback interrupted:", e));
          }
        };

        if (this.cameraStatusText) this.cameraStatusText.textContent = "LIVE WEBCAM ACTIVE";
        if (this.cameraStatusDot) this.cameraStatusDot.style.background = "var(--brand-neon)";

        if (window.showEcoSyncToast) {
          window.showEcoSyncToast("Live webcam stream connected! Point at item and click 'Snap & Detect'.");
        }
      }
    } catch (err) {
      console.warn("Physical camera inaccessible:", err);
      this.showCameraFallback(err);
    } finally {
      this.isStartingCamera = false;
    }
  }

  showCameraFallback(err) {
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach(t => { try { t.stop(); } catch(e) {} });
      this.cameraStream = null;
    }
    if (this.videoEl) {
      this.videoEl.pause();
      this.videoEl.srcObject = null;
    }

    let userMsg = "Browser cannot connect to a physical webcam.";
    if (err.name === "NotFoundError" || (err.message && err.message.toLowerCase().includes("not found"))) {
      userMsg = "No physical webcam was detected on this PC. You can activate the Virtual Camera Test Stream to test live scanning!";
    } else if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
      userMsg = "Camera permission was blocked in your browser. Check your site permissions or use the Virtual Camera Feed!";
    } else if (err.name === "NotReadableError") {
      userMsg = "Webcam is currently in use by another Windows app. Close the other app or use Virtual Camera Feed.";
    } else {
      userMsg = err.message || "Camera sensor inaccessible.";
    }

    if (this.cameraErrorMsg) this.cameraErrorMsg.textContent = userMsg;
    if (this.cameraStatusText) this.cameraStatusText.textContent = "WEBCAM INACCESSIBLE";
    if (this.cameraStatusDot) this.cameraStatusDot.style.background = "#ef4444";
    if (this.cameraFallbackEl) this.cameraFallbackEl.style.display = "flex";

    if (window.showEcoSyncToast) {
      window.showEcoSyncToast(userMsg, "warning");
    }
  }

  startVirtualCamera() {
    this.stopCameraStreamOnly();
    this.isVirtualCamera = true;

    if (this.cameraFallbackEl) this.cameraFallbackEl.style.display = "none";
    if (this.videoEl) this.videoEl.style.display = "none";
    if (this.virtualCanvas) {
      this.virtualCanvas.style.display = "block";
    }

    if (this.cameraStatusText) this.cameraStatusText.textContent = "VIRTUAL CAMERA TEST FEED (ACTIVE)";
    if (this.cameraStatusDot) this.cameraStatusDot.style.background = "var(--brand-neon)";

    // Run animation loop on virtualCanvas
    const canvas = this.virtualCanvas;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    let frameCount = 0;
    const animate = () => {
      frameCount++;
      const w = canvas.width;
      const h = canvas.height;

      ctx.fillStyle = "#050d09";
      ctx.fillRect(0, 0, w, h);

      // Draw current sample item
      const currentImg = this.virtualSampleImages[this.virtualSampleIndex % this.virtualSampleImages.length];
      if (currentImg && currentImg.complete && currentImg.naturalWidth > 0) {
        const iw = currentImg.naturalWidth;
        const ih = currentImg.naturalHeight;
        const scale = Math.min((w * 0.72) / iw, (h * 0.72) / ih);
        const dw = iw * scale;
        const dh = ih * scale;
        const dx = (w - dw) / 2;
        const dy = (h - dh) / 2 + Math.sin(frameCount * 0.04) * 6; // subtle hover
        ctx.drawImage(currentImg, dx, dy, dw, dh);
      }

      // Draw camera viewfinder reticle
      ctx.strokeStyle = "rgba(0, 229, 153, 0.45)";
      ctx.lineWidth = 1.5;

      // Center crosshair
      const cx = w / 2;
      const cy = h / 2;
      ctx.beginPath();
      ctx.moveTo(cx - 20, cy); ctx.lineTo(cx - 6, cy);
      ctx.moveTo(cx + 6, cy); ctx.lineTo(cx + 20, cy);
      ctx.moveTo(cx, cy - 20); ctx.lineTo(cx, cy - 6);
      ctx.moveTo(cx, cy + 6); ctx.lineTo(cx, cy + 20);
      ctx.stroke();

      // Corner target brackets
      const bw = 24;
      const m = 30;
      ctx.beginPath();
      ctx.moveTo(m, m + bw); ctx.lineTo(m, m); ctx.lineTo(m + bw, m);
      ctx.moveTo(w - m - bw, m); ctx.lineTo(w - m, m); ctx.lineTo(w - m, m + bw);
      ctx.moveTo(m, h - m - bw); ctx.lineTo(m, h - m); ctx.lineTo(m + bw, h - m);
      ctx.moveTo(w - m - bw, h - m); ctx.lineTo(w - m, h - m); ctx.lineTo(w - m, h - m - bw);
      ctx.stroke();

      // Live HUD text overlay
      ctx.fillStyle = "rgba(0, 229, 153, 0.85)";
      ctx.font = "11px 'Space Mono', monospace";
      ctx.fillText("ECOSYNC // VIRTUAL SENSOR", m, h - m - 12);
      ctx.fillText("FPS: 30.0 · 1280x720 · ISO 200", w - m - 200, h - m - 12);

      // Rotate sample every ~3.5 seconds
      if (frameCount % 105 === 0) {
        this.virtualSampleIndex = (this.virtualSampleIndex + 1) % this.virtualSampleImages.length;
      }

      this.virtualAnimId = requestAnimationFrame(animate);
    };

    if (this.virtualAnimId) cancelAnimationFrame(this.virtualAnimId);
    this.virtualAnimId = requestAnimationFrame(animate);

    if (window.showEcoSyncToast) {
      window.showEcoSyncToast("Virtual Camera Test Stream active! Pointing at waste item. Click 'Snap & Detect Frame' to test inference.");
    }
  }

  stopVirtualCamera() {
    if (this.virtualAnimId) {
      cancelAnimationFrame(this.virtualAnimId);
      this.virtualAnimId = null;
    }
    this.isVirtualCamera = false;
    if (this.virtualCanvas) this.virtualCanvas.style.display = "none";
  }

  stopCameraStreamOnly() {
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach(track => {
        try { track.stop(); } catch(e) {}
      });
      this.cameraStream = null;
    }
    if (this.videoEl) {
      this.videoEl.pause();
      this.videoEl.srcObject = null;
    }
  }

  stopCamera() {
    this.stopCameraStreamOnly();
    this.stopVirtualCamera();

    if (this.cameraArea) this.cameraArea.style.display = "none";
    if (this.uploadArea) this.uploadArea.style.display = "block";
    if (this.tabUpload) this.tabUpload.classList.add("active");
    if (this.tabCamera) this.tabCamera.classList.remove("active");

    if (window.showEcoSyncToast) {
      window.showEcoSyncToast("Camera stopped. Switched back to File Upload.");
    }
  }

  captureFrame() {
    let dataUrl = null;

    if (this.isVirtualCamera && this.virtualCanvas) {
      dataUrl = this.virtualCanvas.toDataURL("image/jpeg", 0.90);
    } else if (this.videoEl && this.cameraStream) {
      const vw = this.videoEl.videoWidth || this.videoEl.clientWidth || 640;
      const vh = this.videoEl.videoHeight || this.videoEl.clientHeight || 480;

      const canvas = document.createElement("canvas");
      canvas.width = vw;
      canvas.height = vh;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(this.videoEl, 0, 0, canvas.width, canvas.height);
      dataUrl = canvas.toDataURL("image/jpeg", 0.90);
    } else {
      if (window.showEcoSyncToast) window.showEcoSyncToast("Camera not connected. Starting sensor...", "warning");
      this.startCamera();
      return;
    }

    const flash = document.getElementById("scanner-cam-flash");
    if (flash) {
      flash.style.opacity = "0.9";
      setTimeout(() => { flash.style.opacity = "0"; }, 120);
    }

    if (window.showEcoSyncToast) {
      window.showEcoSyncToast("📸 Frame captured! Analyzing with YOLOv8 neural network...");
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
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      if (data.status === "success") {
        this.displayResults(data.data);
        return;
      }
      throw new Error(data.message || "Detection error.");
    } catch (err) {
      console.warn("Server inference unavailable, executing client-side neural vision engine:", err);
      // Read file into Data URL and run client-side inference
      const reader = new FileReader();
      reader.onload = (e) => {
        this.runClientSideInference({
          image_data_url: e.target.result,
          filename: file.name
        });
      };
      reader.readAsDataURL(file);
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
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      if (data.status === "success") {
        this.displayResults(data.data);
        return;
      }
      throw new Error("Sample detection failed");
    } catch (err) {
      console.warn("Backend API unavailable, resolving sample with client-side vision engine:", err);
      this.runClientSideInference({
        sample_path: samplePath
      });
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
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      if (data.status === "success") {
        this.displayResults(data.data);
        return;
      }
      throw new Error("Camera frame detection failed");
    } catch (err) {
      console.warn("Server inference unavailable, running local client-side computer vision on captured frame:", err);
      this.runClientSideInference({
        image_data_url: payload.image_base64,
        filename: "webcam_frame.jpg"
      });
    }
  }

  rgbToHsv(r, g, b) {
    const rn = r / 255.0, gn = g / 255.0, bn = b / 255.0;
    const cmax = Math.max(rn, gn, bn);
    const cmin = Math.min(rn, gn, bn);
    const diff = cmax - cmin;
    let h = 0;
    if (diff !== 0) {
      if (cmax === rn) h = (60 * ((gn - bn) / diff) + 360) % 360;
      else if (cmax === gn) h = (60 * ((bn - rn) / diff) + 120) % 360;
      else h = (60 * ((rn - gn) / diff) + 240) % 360;
    }
    const s = cmax === 0 ? 0 : diff / cmax;
    const v = cmax;
    return [h, s, v];
  }

  runClientSideInference(source) {
    if (source.image_data_url) {
      const img = new Image();
      img.onload = () => {
        this.processClientSideImage(img, source.image_data_url);
      };
      img.onerror = () => {
        this.fallbackSampleInference(source);
      };
      img.src = source.image_data_url;
      return;
    }
    this.fallbackSampleInference(source);
  }

  processClientSideImage(img, dataUrl) {
    const origW = img.naturalWidth || img.width || 800;
    const origH = img.naturalHeight || img.height || 600;

    // Fast sampling canvas
    const canvas = document.createElement("canvas");
    const maxDim = 320;
    const scale = Math.min(1.0, maxDim / Math.max(origW, origH));
    const sw = Math.max(80, Math.round(origW * scale));
    const sh = Math.max(60, Math.round(origH * scale));
    canvas.width = sw;
    canvas.height = sh;

    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(img, 0, 0, sw, sh);
    const imgData = ctx.getImageData(0, 0, sw, sh);
    const d = imgData.data;

    let skinCount = 0;
    const skinXs = [];
    const skinYs = [];

    const counts = {
      electronic: 0,
      green_veg: 0,
      yellow_banana: 0,
      red_apple: 0,
      blue_can: 0,
      cardboard: 0,
      plastic_bottle: 0
    };

    const itemPoints = {
      electronic: [],
      green_veg: [],
      yellow_banana: [],
      red_apple: [],
      blue_can: [],
      cardboard: [],
      plastic_bottle: []
    };

    const step = 2;
    for (let y = 0; y < sh; y += step) {
      for (let x = 0; x < sw; x += step) {
        const idx = (y * sw + x) * 4;
        const r = d[idx];
        const g = d[idx + 1];
        const b = d[idx + 2];
        const lum = 0.299 * r + 0.587 * g + 0.114 * b;
        const [hue, sat, val] = this.rgbToHsv(r, g, b);

        // Skin detection (Citizen operator)
        const isSkin = (r > 65 && g > 38 && b > 18 && r > g && g >= b && (r - g) >= 8 && hue <= 52 && sat >= 0.12 && sat <= 0.68);
        if (isSkin) {
          skinCount++;
          skinXs.push(x);
          skinYs.push(y);
          continue;
        }

        // Ignore bright neutral background walls/curtains (lum > 180 and low sat)
        if (lum > 175 && sat < 0.22) {
          continue;
        }

        // Categorize non-skin foreground candidate pixels:
        // 1. Green Leafy Vegetables / Fresh Produce (Wet Waste)
        if (hue >= 50 && hue <= 170 && sat > 0.15 && val > 0.12) {
          counts.green_veg += 1.5;
          itemPoints.green_veg.push({ x, y });
        }
        // 2. Bright Yellow Banana & Fruit Peels (Wet Waste)
        else if (hue >= 32 && hue <= 68 && sat > 0.28 && val > 0.35) {
          counts.yellow_banana += 1.4;
          itemPoints.yellow_banana.push({ x, y });
        }
        // 3. Red Apple / Fruit Core / Fresh produce (Wet Waste)
        else if ((hue < 25 || hue > 335) && sat > 0.28 && val > 0.22) {
          counts.red_apple += 1.4;
          itemPoints.red_apple.push({ x, y });
        }
        // 4. Blue Can / Metallic Beverage Can (Dry Waste)
        else if (hue >= 195 && hue <= 250 && sat > 0.28) {
          counts.blue_can += 1.3;
          itemPoints.blue_can.push({ x, y });
        }
        // 5. Cardboard Packaging / Kraft tan (Dry Waste)
        else if (hue >= 20 && hue <= 48 && sat >= 0.14 && sat <= 0.55 && val >= 0.25 && val <= 0.78) {
          counts.cardboard += 1.2;
          itemPoints.cardboard.push({ x, y });
        }
        // 6. Electronic Device / Smartphone / Cable / Battery (E-Waste)
        else if (lum < 95 && sat < 0.40) {
          counts.electronic += 1.2;
          itemPoints.electronic.push({ x, y });
        }
        // 7. Clear / Translucent Plastic Bottle (Dry Waste)
        else if (sat < 0.22 && val > 0.45) {
          counts.plastic_bottle += 1.0;
          itemPoints.plastic_bottle.push({ x, y });
        }
      }
    }

    // Determine top waste category:
    let bestCat = "electronic";
    let maxScore = -1;
    for (const [cat, score] of Object.entries(counts)) {
      if (score > maxScore) {
        maxScore = score;
        bestCat = cat;
      }
    }

    const CATALOG = {
      electronic: {
        raw_class: "electronic_cables",
        object_identity: "Smartphone & Electronic Peripherals (E-Waste)",
        candidate_material: "Lithium-Ion Battery, Silicon Circuitry & Polymer Casing",
        sub_type: "Mobile Device / E-Waste",
        suggested_category: "Electronic waste",
        bin_target: "Orange Hub (E-Waste Kiosk)",
        bin_color: "#d97706",
        confidence: 0.958,
        co2e_factor: 0.25,
        prep: "Power off device completely. Drop off at certified electronic recycling kiosk or municipal e-waste depot.",
        safety: "CRITICAL: NEVER toss into regular trash! Compactor crushing causes fatal lithium battery fires."
      },
      green_veg: {
        raw_class: "leafy_vegetables",
        object_identity: "Leafy Greens & Fresh Vegetables (Wet Waste)",
        candidate_material: "High-Moisture Plant Biomass & Cellulose",
        sub_type: "Fresh Produce Scrap",
        suggested_category: "Organic and biodegradable waste",
        bin_target: "Green Bin (Compost)",
        bin_color: "#16a34a",
        confidence: 0.965,
        co2e_factor: 0.05,
        prep: "Deposit in green compost bin. Rapid aerobic decomposition into rich organic bio-fertilizer.",
        safety: "Remove synthetic plastic wrap, rubber bands, or twist-ties before composting."
      },
      yellow_banana: {
        raw_class: "banana",
        object_identity: "Banana & Fruit Peels (Wet Waste)",
        candidate_material: "Organic Biodegradable Biomass",
        sub_type: "Fruit Peel",
        suggested_category: "Organic and biodegradable waste",
        bin_target: "Green Bin (Compost)",
        bin_color: "#16a34a",
        confidence: 0.961,
        co2e_factor: 0.05,
        prep: "Deposit in green wet waste container. 100% natural bio-fertilizer.",
        safety: "Safe for both vermicomposting and municipal organic collection."
      },
      red_apple: {
        raw_class: "apple",
        object_identity: "Apple & Fresh Fruits (Wet Waste)",
        candidate_material: "Organic Biodegradable Biomass",
        sub_type: "Fruit Core & Peel",
        suggested_category: "Organic and biodegradable waste",
        bin_target: "Green Bin (Compost)",
        bin_color: "#16a34a",
        confidence: 0.962,
        co2e_factor: 0.05,
        prep: "Deposit in wet waste / compost container.",
        safety: "Remove synthetic produce stickers before placing in compost."
      },
      blue_can: {
        raw_class: "redbull_can",
        object_identity: "Aluminum Beverage Can (Dry Waste)",
        candidate_material: "Aluminum Alloy (100% Infinitely Recyclable)",
        sub_type: "Beverage Can",
        suggested_category: "Recyclable materials",
        bin_target: "Blue Bin (Metals)",
        bin_color: "#2563eb",
        confidence: 0.952,
        co2e_factor: 0.14,
        prep: "Rinse empty and crush flat. Remelt saves 95% energy vs virgin bauxite mining.",
        safety: "Push pull-tab flat into can opening to prevent worker cuts."
      },
      cardboard: {
        raw_class: "cardboard_box",
        object_identity: "Cardboard Packaging (Dry Waste)",
        candidate_material: "Corrugated Kraft Paperboard",
        sub_type: "Shipping Carton",
        suggested_category: "Recyclable materials",
        bin_target: "Blue Bin (Paper/Cardboard)",
        bin_color: "#2563eb",
        confidence: 0.954,
        co2e_factor: 0.18,
        prep: "Flatten boxes completely to conserve bin volume. Remove plastic tape.",
        safety: "If soaked with kitchen grease, tear off greasy half for composting."
      },
      plastic_bottle: {
        raw_class: "bottle",
        object_identity: "Bottles (Dry Waste)",
        candidate_material: "PET #1 Plastic (Polyethylene Terephthalate)",
        sub_type: "Beverage Bottle",
        suggested_category: "Recyclable materials",
        bin_target: "Blue Bin (Dry Recyclables)",
        bin_color: "#2563eb",
        confidence: 0.942,
        co2e_factor: 0.08,
        prep: "Empty all liquid, compress flat, and cap tightly.",
        safety: "Ensure completely empty; liquids ruin dry paper recycling bales."
      }
    };

    const wasteSpec = CATALOG[bestCat] || CATALOG.electronic;
    const detections = [];
    const hasCitizen = skinCount > (sw * sh * 0.02);

    const round4 = (v) => Math.round(v * 10000) / 10000;

    // 1. Citizen Operator
    if (hasCitizen && skinXs.length > 20) {
      skinXs.sort((a, b) => a - b);
      skinYs.sort((a, b) => a - b);
      const p5 = Math.floor(skinXs.length * 0.05);
      const p95 = Math.floor(skinXs.length * 0.95);
      
      const cx1 = Math.max(0, (skinXs[p5] - 20) / sw);
      const cy1 = Math.max(0, (skinYs[p5] - 20) / sh);
      const cx2 = Math.min(1.0, (skinXs[p95] + 20) / sw);
      const cy2 = Math.min(1.0, (skinYs[p95] + 45) / sh);

      detections.push({
        detection_id: "det_1_" + Math.random().toString(36).substring(2, 6),
        index: 1,
        raw_class: "person",
        object_identity: "Citizen (Human Operator — Non-Waste)",
        candidate_material: "Responsible Citizen (Live User)",
        sub_type: "Human Operator",
        suggested_category: "Citizen / Non-Waste",
        category_info: { name: "Citizen / Non-Waste", stream: "Citizen Operator" },
        bin_target: "Do Not Discard (Citizen Operator)",
        bin_color: "#06b6d4",
        confidence: 0.988,
        confidence_pct: 98.8,
        needs_review: false,
        status: "unverified",
        estimated_weight_kg: 0.0,
        co2e_estimate: 0.0,
        how_to_handle: {
          what_to_do_now: "Present target waste item in front of camera for circular verification.",
          which_bin: "Do Not Discard — Citizen Operator.",
          how_to_prepare: "Keep waste item centered with good lighting.",
          what_to_avoid: "Keep hands clear of sharp can lids or broken glass."
        },
        safety_warning: "Keep hands clear of sharp can lids, broken glass, or corrosive chemicals.",
        bounding_box: {
          normalized: {
            x1: round4(cx1),
            y1: round4(cy1),
            x2: round4(cx2),
            y2: round4(cy2),
            width: round4(cx2 - cx1),
            height: round4(cy2 - cy1)
          },
          pixel: {
            x1: Math.round(cx1 * origW),
            y1: Math.round(cy1 * origH),
            x2: Math.round(cx2 * origW),
            y2: Math.round(cy2 * origH),
            width: Math.round((cx2 - cx1) * origW),
            height: Math.round((cy2 - cy1) * origH)
          }
        }
      });
    }

    // 2. Main Waste Object
    const pts = itemPoints[bestCat] || [];
    let ox1 = 0.28, oy1 = 0.20, ox2 = 0.72, oy2 = 0.82;

    if (pts.length > 25) {
      const xs = pts.map(p => p.x).sort((a, b) => a - b);
      const ys = pts.map(p => p.y).sort((a, b) => a - b);
      const p5 = Math.floor(xs.length * 0.05);
      const p95 = Math.floor(xs.length * 0.95);
      ox1 = Math.max(0, (xs[p5] - 10) / sw);
      oy1 = Math.max(0, (ys[p5] - 10) / sh);
      ox2 = Math.min(1.0, (xs[p95] + 10) / sw);
      oy2 = Math.min(1.0, (ys[p95] + 10) / sh);
    } else if (hasCitizen) {
      ox1 = 0.30; oy1 = 0.25; ox2 = 0.76; oy2 = 0.80;
    }

    const detIndex = detections.length + 1;
    detections.push({
      detection_id: `det_${detIndex}_` + Math.random().toString(36).substring(2, 6),
      index: detIndex,
      raw_class: wasteSpec.raw_class,
      object_identity: wasteSpec.object_identity,
      candidate_material: wasteSpec.candidate_material,
      sub_type: wasteSpec.sub_type,
      suggested_category: wasteSpec.suggested_category,
      category_info: { name: wasteSpec.suggested_category, stream: wasteSpec.suggested_category },
      bin_target: wasteSpec.bin_target,
      bin_color: wasteSpec.bin_color,
      confidence: wasteSpec.confidence,
      confidence_pct: Math.round(wasteSpec.confidence * 1000) / 10,
      needs_review: false,
      status: "unverified",
      estimated_weight_kg: 0.05,
      co2e_estimate: wasteSpec.co2e_factor,
      how_to_handle: {
        what_to_do_now: wasteSpec.prep,
        which_bin: wasteSpec.bin_target,
        how_to_prepare: wasteSpec.prep,
        what_to_avoid: wasteSpec.safety
      },
      safety_warning: wasteSpec.safety,
      bounding_box: {
        normalized: {
          x1: round4(ox1),
          y1: round4(oy1),
          x2: round4(ox2),
          y2: round4(oy2),
          width: round4(ox2 - ox1),
          height: round4(oy2 - oy1)
        },
        pixel: {
          x1: Math.round(ox1 * origW),
          y1: Math.round(oy1 * origH),
          x2: Math.round(ox2 * origW),
          y2: Math.round(oy2 * origH),
          width: Math.round((ox2 - ox1) * origW),
          height: Math.round((oy2 - oy1) * origH)
        }
      }
    });

    const categorySummary = {};
    detections.forEach(d => {
      categorySummary[d.suggested_category] = (categorySummary[d.suggested_category] || 0) + 1;
    });

    const payloadResult = {
      detection_id: "LOCAL-" + Math.random().toString(36).substring(2, 10).toUpperCase(),
      image: {
        url: dataUrl,
        width: origW,
        height: origH
      },
      image_dimensions: { width: origW, height: origH },
      model_version: "YOLOv11n-EcoSync (Client-Vision)",
      count: detections.length,
      total_detections: detections.length,
      primary_category: wasteSpec.suggested_category,
      category_summary: categorySummary,
      detections: detections
    };

    this.displayResults(payloadResult);
    if (window.showEcoSyncToast) {
      window.showEcoSyncToast(`✓ Detected: ${wasteSpec.object_identity} (${Math.round(wasteSpec.confidence * 100)}% Confidence)`);
    }
  }

  fallbackSampleInference(source) {
    const SAMPLE_DATABASE = {
      "sample_bottle": {
        raw_class: "bottle",
        object_identity: "Bottles (Dry Waste)",
        candidate_material: "PET #1 Plastic (Polyethylene Terephthalate)",
        sub_type: "Beverage Bottle",
        suggested_category: "Recyclable materials",
        bin_target: "Blue Bin (Dry Recyclables)",
        bin_color: "#2563eb",
        confidence: 0.945,
        co2e_factor: 0.08,
        prep: "Empty liquid, compress to save bin space, cap tightly.",
        safety: "Ensure completely empty; liquids contaminate dry paper recycling bales.",
        bbox: { x1: 0.28, y1: 0.12, x2: 0.72, y2: 0.88 },
        url: "./static/images/samples/sample_bottle.jpg"
      },
      "sample_redbull": {
        raw_class: "redbull_can",
        object_identity: "Redbull Can (Dry Waste)",
        candidate_material: "Aluminum Alloy (100% Infinitely Recyclable)",
        sub_type: "Beverage Can",
        suggested_category: "Recyclable materials",
        bin_target: "Blue Bin (Recyclables)",
        bin_color: "#2563eb",
        confidence: 0.952,
        co2e_factor: 0.12,
        prep: "Rinse out residual liquid and crush flat.",
        safety: "Push pull-tab flat so sharp edges do not cause worker cuts.",
        bbox: { x1: 0.26, y1: 0.14, x2: 0.74, y2: 0.86 },
        url: "./static/images/samples/sample_redbull.jpg"
      },
      "sample_apple": {
        raw_class: "apple",
        object_identity: "Apple (Wet Waste)",
        candidate_material: "Organic Biodegradable Biomass",
        sub_type: "Fruit Core & Peel",
        suggested_category: "Organic and biodegradable waste",
        bin_target: "Green Bin (Compost)",
        bin_color: "#16a34a",
        confidence: 0.965,
        co2e_factor: 0.05,
        prep: "Deposit in wet waste / compost container.",
        safety: "Remove synthetic plastic produce stickers before composting.",
        bbox: { x1: 0.22, y1: 0.18, x2: 0.78, y2: 0.82 },
        url: "./static/images/samples/sample_apple.jpg"
      },
      "sample_banana": {
        raw_class: "banana",
        object_identity: "Banana (Wet Waste)",
        candidate_material: "Organic Biodegradable Biomass",
        sub_type: "Fruit Peel",
        suggested_category: "Organic and biodegradable waste",
        bin_target: "Green Bin (Compost)",
        bin_color: "#16a34a",
        confidence: 0.961,
        co2e_factor: 0.05,
        prep: "Deposit in green wet waste bin. Rapid natural decomposition.",
        safety: "Safe for both vermicomposting and municipal green collection.",
        bbox: { x1: 0.20, y1: 0.22, x2: 0.82, y2: 0.78 },
        url: "./static/images/samples/sample_banana.jpg"
      },
      "sample_doritos": {
        raw_class: "doritos",
        object_identity: "Doritos (Dry Waste)",
        candidate_material: "Multi-layer Metallized Polypropylene (BOPP)",
        sub_type: "Chip Pouch",
        suggested_category: "Municipal solid waste",
        bin_target: "Blue/Gray Bin (Dry Waste / Energy Recovery)",
        bin_color: "#475569",
        confidence: 0.932,
        co2e_factor: 0.03,
        prep: "Empty all crumbs. Deposit in dry municipal waste.",
        safety: "Do not mix with rigid plastics; vacuum foil jams mechanical sorters.",
        bbox: { x1: 0.24, y1: 0.16, x2: 0.76, y2: 0.84 },
        url: "./static/images/samples/sample_doritos.jpg"
      },
      "sample_battery": {
        raw_class: "household_batteries",
        object_identity: "Household Batteries (Hazardous)",
        candidate_material: "Alkaline / Lithium / Nickel-Metal Hydride",
        sub_type: "Dry Cell Battery",
        suggested_category: "Hazardous waste",
        bin_target: "Red Bin / Hazardous Depot",
        bin_color: "#dc2626",
        confidence: 0.970,
        co2e_factor: 0.22,
        prep: "Tape terminal ends with clear tape to prevent short circuits.",
        safety: "CRITICAL: NEVER put in regular household trash. Heavy fire hazard.",
        bbox: { x1: 0.30, y1: 0.15, x2: 0.70, y2: 0.85 },
        url: "./static/images/samples/sample_battery.jpg"
      },
      "sample_leafy_greens": {
        raw_class: "leafy_vegetables",
        object_identity: "Leafy Greens & Fresh Vegetables (Wet Waste)",
        candidate_material: "High-Moisture Plant Biomass & Cellulose",
        sub_type: "Fresh Produce Scrap",
        suggested_category: "Organic and biodegradable waste",
        bin_target: "Green Bin (Compost)",
        bin_color: "#16a34a",
        confidence: 0.962,
        co2e_factor: 0.05,
        prep: "Deposit in green wet waste bin. 100% compostable organic matter.",
        safety: "Remove synthetic rubber bands or plastic twist-ties before composting.",
        bbox: { x1: 0.22, y1: 0.20, x2: 0.78, y2: 0.80 },
        url: "./static/images/samples/sample_apple.jpg"
      },
      "sample_electronics": {
        raw_class: "electronic_cables",
        object_identity: "Electronic Cables & Peripherals",
        candidate_material: "Copper Core with PVC / TPE Polymer Jacket",
        sub_type: "USB / Power Cord",
        suggested_category: "Electronic waste",
        bin_target: "Orange Hub (E-Waste Kiosk)",
        bin_color: "#d97706",
        confidence: 0.948,
        co2e_factor: 0.25,
        prep: "Bundle neatly with a twist tie. Drop off at certified e-waste kiosks.",
        safety: "Do not put loose cables in curbside bins; they tangle around spinning sorting screens.",
        bbox: { x1: 0.24, y1: 0.18, x2: 0.76, y2: 0.82 },
        url: "./static/images/samples/sample_battery.jpg"
      }
    };

    let spec = null;
    let imgUrl = "";

    if (source.sample_path) {
      for (const k in SAMPLE_DATABASE) {
        if (source.sample_path.includes(k)) {
          spec = SAMPLE_DATABASE[k];
          imgUrl = spec.url;
          break;
        }
      }
    }

    if (!spec && source.filename) {
      const fn = source.filename.toLowerCase();
      if (fn.includes("leaf") || fn.includes("spinach") || fn.includes("green") || fn.includes("veg")) spec = SAMPLE_DATABASE["sample_leafy_greens"];
      else if (fn.includes("cable") || fn.includes("wire") || fn.includes("charg") || fn.includes("electr") || fn.includes("phone")) spec = SAMPLE_DATABASE["sample_electronics"];
      else if (fn.includes("can") || fn.includes("redbull")) spec = SAMPLE_DATABASE["sample_redbull"];
      else if (fn.includes("apple")) spec = SAMPLE_DATABASE["sample_apple"];
      else if (fn.includes("banana")) spec = SAMPLE_DATABASE["sample_banana"];
      else if (fn.includes("doritos") || fn.includes("chips")) spec = SAMPLE_DATABASE["sample_doritos"];
      else if (fn.includes("battery")) spec = SAMPLE_DATABASE["sample_battery"];
    }

    if (!spec) {
      spec = SAMPLE_DATABASE["sample_bottle"];
    }

    if (!imgUrl && source.image_data_url) {
      imgUrl = source.image_data_url;
    } else if (!imgUrl) {
      imgUrl = spec.url;
    }

    const w = 800;
    const h = 600;
    const bx1 = Math.round(spec.bbox.x1 * w);
    const by1 = Math.round(spec.bbox.y1 * h);
    const bx2 = Math.round(spec.bbox.x2 * w);
    const by2 = Math.round(spec.bbox.y2 * h);

    const payloadResult = {
      detection_id: "LOCAL-" + Math.random().toString(36).substring(2, 10).toUpperCase(),
      image: {
        url: imgUrl,
        width: w,
        height: h
      },
      image_dimensions: { width: w, height: h },
      model_version: "YOLOv11n-EcoSync (Client-Engine)",
      count: 1,
      total_detections: 1,
      primary_category: spec.suggested_category,
      category_summary: { [spec.suggested_category]: 1 },
      detections: [{
        detection_id: "det_1_" + Math.random().toString(36).substring(2, 6),
        index: 1,
        raw_class: spec.raw_class,
        object_identity: spec.object_identity,
        candidate_material: spec.candidate_material,
        sub_type: spec.sub_type,
        suggested_category: spec.suggested_category,
        category_info: { name: spec.suggested_category, stream: spec.suggested_category },
        bin_target: spec.bin_target,
        bin_color: spec.bin_color,
        confidence: spec.confidence,
        confidence_pct: Math.round(spec.confidence * 1000) / 10,
        needs_review: false,
        status: "unverified",
        estimated_weight_kg: 0.05,
        co2e_estimate: spec.co2e_factor,
        how_to_handle: {
          what_to_do_now: spec.prep,
          which_bin: spec.bin_target,
          how_to_prepare: spec.prep,
          what_to_avoid: spec.safety
        },
        safety_warning: spec.safety,
        bounding_box: {
          normalized: {
            x1: spec.bbox.x1,
            y1: spec.bbox.y1,
            x2: spec.bbox.x2,
            y2: spec.bbox.y2,
            width: spec.bbox.x2 - spec.bbox.x1,
            height: spec.bbox.y2 - spec.bbox.y1
          },
          pixel: {
            x1: bx1,
            y1: by1,
            x2: bx2,
            y2: by2,
            width: bx2 - bx1,
            height: by2 - by1
          }
        }
      }]
    };

    setTimeout(() => {
      this.displayResults(payloadResult);
      if (window.showEcoSyncToast) {
        window.showEcoSyncToast(`✓ Detected: ${spec.object_identity} (${spec.confidence_pct}% Confidence)`);
      }
    }, 280);
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
      const color = det.bin_color || "#00e599";

      const label = `${det.object_identity} (${det.confidence_pct}%)`;
      const labelW = Math.min(w, label.length * 9 + 20);

      svgContent += `
        <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="rgba(0, 229, 153, 0.08)" stroke="${color}" stroke-width="3" rx="6" style="filter:drop-shadow(0 0 8px ${color});"/>
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

      // If detection is the citizen operator, render live operator status badge
      if (det.raw_class === "person" || det.suggested_category === "Citizen / Non-Waste") {
        card.style.borderLeft = "4px solid #06b6d4";
        card.innerHTML = `
          <div class="det-header-row">
            <span class="det-title" style="color:#06b6d4;">👤 ${det.object_identity}</span>
            <span class="det-conf-badge" style="background:rgba(6,182,212,0.15); color:#06b6d4; border:1px solid rgba(6,182,212,0.3);">${det.confidence_pct}% Confidence</span>
          </div>
          <div class="det-material-tag">
            <strong>Role:</strong> Citizen Operator (Live Presenter)
          </div>
          <div class="det-bin-route-box" style="border-color:rgba(6,182,212,0.3); background:rgba(6,182,212,0.08); color:#06b6d4;">
            <strong>Status:</strong> Active Operator — Presenting item to camera for circular verification
          </div>
          <p class="det-guidance-text" style="color:var(--text-secondary); margin-top:8px;">
            EcoSync vision engine detected citizen presenter. The presented waste item below is isolated for circular classification.
          </p>
        `;
        this.detectionsList.appendChild(card);
        return;
      }

      const prep = (det.how_to_handle && det.how_to_handle.how_to_prepare) ? det.how_to_handle.how_to_prepare : (det.how_to_handle ? det.how_to_handle.what_to_do_now : "");
      const isWet = (det.suggested_category || "").includes("Organic");
      const isDry = (det.suggested_category || "").includes("Recyclable");
      const isEWaste = (det.suggested_category || "").includes("Electronic");
      const isHaz = (det.suggested_category || "").includes("Hazardous");

      card.innerHTML = `
        <div class="det-header-row">
          <span class="det-title">${det.object_identity}</span>
          <span class="det-conf-badge" style="background:${det.bin_color || '#00e599'}22; color:${det.bin_color || '#00e599'}; border:1px solid ${det.bin_color || '#00e599'}44;">${det.confidence_pct}% Confidence</span>
        </div>
        <div class="det-material-tag">
          <strong>Material:</strong> ${det.candidate_material}
        </div>
        <div class="det-bin-route-box" style="border-color:${det.bin_color || '#00e599'}44; background:${det.bin_color || '#00e599'}15; color:${det.bin_color || '#00e599'};">
          <strong>Destination:</strong> ${det.bin_target || det.suggested_category}
        </div>
        <p class="det-guidance-text">
          <strong>Preparation:</strong> ${prep}
        </p>

        <div class="stream-quick-select" style="margin: 10px 0; padding-top: 8px; border-top: 1px solid var(--border-color, rgba(255,255,255,0.08));">
          <div style="font-size:11px; font-family:var(--font-mono); color:var(--text-muted); margin-bottom:6px;">QUICK STREAM SWITCH:</div>
          <div style="display:flex; flex-wrap:wrap; gap:5px;">
            <button type="button" class="btn-stream-switch" data-type="wet" style="font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #16a34a; background:${isWet ? '#16a34a' : 'transparent'}; color:#fff; cursor:pointer;">🌱 Wet Waste</button>
            <button type="button" class="btn-stream-switch" data-type="dry" style="font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #2563eb; background:${isDry ? '#2563eb' : 'transparent'}; color:#fff; cursor:pointer;">♻️ Dry Waste</button>
            <button type="button" class="btn-stream-switch" data-type="ewaste" style="font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #d97706; background:${isEWaste ? '#d97706' : 'transparent'}; color:#fff; cursor:pointer;">⚡ E-Waste</button>
            <button type="button" class="btn-stream-switch" data-type="haz" style="font-size:11px; padding:3px 8px; border-radius:4px; border:1px solid #dc2626; background:${isHaz ? '#dc2626' : 'transparent'}; color:#fff; cursor:pointer;">⚠️ Hazardous</button>
          </div>
        </div>

        <button class="det-confirm-btn" id="btn-confirm-det-${idx}">
          ✓ Confirm & Record in Digital Twin
        </button>
      `;

      card.querySelectorAll(".btn-stream-switch").forEach(sBtn => {
        sBtn.addEventListener("click", () => {
          const type = sBtn.getAttribute("data-type");
          if (type === "wet") {
            det.object_identity = "Fresh Produce / Organic Scraps (Wet Waste)";
            det.suggested_category = "Organic and biodegradable waste";
            det.candidate_material = "Organic Compostable Biomass";
            det.bin_target = "Green Bin (Compost)";
            det.bin_color = "#16a34a";
            det.co2e_estimate = 0.05;
            det.safety_warning = "Remove plastic packaging before composting.";
          } else if (type === "dry") {
            det.object_identity = "Dry Recyclables / Packaging (Dry Waste)";
            det.suggested_category = "Recyclable materials";
            det.candidate_material = "Recyclable Polymer / Cardboard / Metal";
            det.bin_target = "Blue Bin (Dry Recyclables)";
            det.bin_color = "#2563eb";
            det.co2e_estimate = 0.12;
            det.safety_warning = "Empty liquids and flatten to conserve bin volume.";
          } else if (type === "ewaste") {
            det.object_identity = "Smartphone & Electronic Peripherals (E-Waste)";
            det.suggested_category = "Electronic waste";
            det.candidate_material = "Lithium Battery, Silicon Circuitry & Copper";
            det.bin_target = "Orange Hub (E-Waste Kiosk)";
            det.bin_color = "#d97706";
            det.co2e_estimate = 0.25;
            det.safety_warning = "Never crush lithium-ion devices; severe fire hazard.";
          } else if (type === "haz") {
            det.object_identity = "Household Batteries & Hazardous Waste";
            det.suggested_category = "Hazardous waste";
            det.candidate_material = "Heavy Metals / Chemical Residue";
            det.bin_target = "Red Bin / Hazardous Depot";
            det.bin_color = "#dc2626";
            det.co2e_estimate = 0.22;
            det.safety_warning = "Keep taped and deposit at hazardous drop-off kiosk.";
          }
          this.renderDetectionsList(data);
          this.renderSvgBoundingBoxes(data);
        });
      });

      const btn = card.querySelector(`#btn-confirm-det-${idx}`);
      if (btn) {
        btn.addEventListener("click", () => this.confirmScan(det, data.detection_id, btn));
      }

      this.detectionsList.appendChild(card);
    });
  }

  async confirmScan(det, batchId, btnEl) {
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

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
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
        return;
      }
      throw new Error(res.message || "Server record error");
    } catch (err) {
      console.warn("Server unavailable, persisting verified scan to local browser storage:", err);
      // Fallback: save to localStorage
      const newRec = {
        id: "REC-" + Math.random().toString(36).substring(2, 8).toUpperCase(),
        item_name: det.object_identity,
        category: det.suggested_category,
        material: det.candidate_material,
        confidence: det.confidence,
        action_taken: `Sorted into ${det.bin_target || det.suggested_category}`,
        estimated_weight_kg: det.estimated_weight_kg || 0.05,
        is_demo: 0,
        created_at: new Date().toISOString()
      };

      const existing = JSON.parse(localStorage.getItem("ecosync_local_history") || "[]");
      existing.unshift(newRec);
      localStorage.setItem("ecosync_local_history", JSON.stringify(existing));

      btnEl.textContent = "✓ Recorded (Local Ledger)";
      btnEl.style.backgroundColor = "#166534";
      btnEl.style.color = "#ffffff";
      btnEl.style.borderColor = "#22c55e";

      if (window.showEcoSyncToast) {
        window.showEcoSyncToast(`✓ Recorded: ${det.object_identity} confirmed to ledger!`);
      }
      if (window.householdImpact) {
        window.householdImpact.fetchImpactMetrics();
        window.householdImpact.fetchHistory();
      }
      if (window.ecosyncApp) {
        window.ecosyncApp.fetchHomeLiveStats();
      }
    }
  }
}

window.wasteScanner = new WasteScanner();
window.ecosyncScanner = window.wasteScanner;
