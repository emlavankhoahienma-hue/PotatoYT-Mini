/**
 * PotatoYT-Mini - Modern Client Engine & HUD Controller
 * Features: Cyber Glassmorphism HUD, SVG Vector Icons, Quick Search Modal,
 * Toast Notifications, AdBlocker & Auto-Skip, Quality & Speed Controllers.
 */

(function () {
    console.log("[PotatoYT] Initializing Cyber HUD Engine...");

    let currentResolution = "480p";
    let isAudioOnly = false;
    let isPinned = true;
    let isGhost = false;
    let currentOpacity = 100;
    let toastTimer = null;

    // SVG Icons
    const ICONS = {
        pin: `<svg viewBox="0 0 24 24"><path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/></svg>`,
        ghost: `<svg viewBox="0 0 24 24"><path d="M12 2C7.58 2 4 5.58 4 10v10l3-2 3 2 2-1.33L14 20l3-2 3 2V10c0-4.42-3.58-8-8-8zm-3 8a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm6 0a1.5 1.5 0 110-3 1.5 1.5 0 010 3z"/></svg>`,
        audio: `<svg viewBox="0 0 24 24"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>`,
        search: `<svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>`,
        home: `<svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>`,
        reload: `<svg viewBox="0 0 24 24"><path d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>`
    };

    // =========================================================================
    // 1. Toast Notification System
    // =========================================================================
    function showToast(text, iconHtml = "") {
        let toast = document.getElementById("potato-toast");
        if (!toast) {
            toast = document.createElement("div");
            toast.id = "potato-toast";
            document.documentElement.appendChild(toast);
        }

        toast.innerHTML = (iconHtml ? `<span style="display:inline-flex; align-items:center;">${iconHtml}</span>` : "") + `<span>${text}</span>`;
        toast.classList.add("show");

        if (toastTimer) clearTimeout(toastTimer);
        toastTimer = setTimeout(() => {
            toast.classList.remove("show");
        }, 2000);
    }

    // =========================================================================
    // 2. HUD Construction
    // =========================================================================
    function createHUD() {
        if (document.getElementById("potato-hud-container")) return;

        const hud = document.createElement("div");
        hud.id = "potato-hud-container";
        hud.innerHTML = `
            <div class="potato-hud-left">
                <div class="potato-brand" title="PotatoYT Mini Player">
                    <span class="potato-brand-dot"></span>
                    <span>PotatoYT</span>
                </div>
                <button id="btn-pin" class="potato-pill-btn active" title="Ghim trên cùng (Ctrl+Alt+T)">
                    ${ICONS.pin}
                    <span>Ghim</span>
                </button>
                <button id="btn-ghost" class="potato-pill-btn" title="Chế độ xuyên thấu chuột (Ctrl+Alt+G)">
                    ${ICONS.ghost}
                    <span>Ghost</span>
                </button>
                <button id="btn-audio" class="potato-pill-btn" title="Tắt hình tiết kiệm 100% GPU (Ctrl+Alt+M)">
                    ${ICONS.audio}
                    <span>Audio</span>
                </button>
                <button id="btn-search-toggle" class="potato-pill-btn" title="Tìm kiếm video / Dán link">
                    ${ICONS.search}
                </button>
            </div>
            <div class="potato-hud-right">
                <select id="sel-quality" class="potato-modern-select" title="Khóa độ phân giải video">
                    <option value="360p">360p</option>
                    <option value="480p" selected>480p</option>
                    <option value="720p">720p</option>
                    <option value="auto">Auto</option>
                </select>
                <select id="sel-speed" class="potato-modern-select" title="Tốc độ phát">
                    <option value="1.0" selected>1.0x</option>
                    <option value="1.25">1.25x</option>
                    <option value="1.5">1.5x</option>
                    <option value="2.0">2.0x</option>
                </select>
                <input id="slider-opacity" class="potato-opacity-slider" type="range" min="20" max="100" value="100" title="Độ trong suốt">
                <span id="txt-opacity" style="font-size:10px; color:#94a3b8; font-weight:700; width:28px;">100%</span>
                <button id="btn-home" class="potato-pill-btn" title="Trang chủ YouTube">${ICONS.home}</button>
                <button id="btn-reload" class="potato-pill-btn" title="Tải lại">${ICONS.reload}</button>
            </div>
        `;

        // Modern Cyber Equalizer Audio Overlay
        const audioOverlay = document.createElement("div");
        audioOverlay.id = "potato-audio-overlay";
        audioOverlay.innerHTML = `
            <div class="potato-eq-container">
                <div class="potato-eq-bar"></div>
                <div class="potato-eq-bar"></div>
                <div class="potato-eq-bar"></div>
                <div class="potato-eq-bar"></div>
                <div class="potato-eq-bar"></div>
            </div>
            <div class="potato-audio-title">Audio Background Mode</div>
            <div class="potato-audio-subtitle">● Đang phát âm thanh — Tiết kiệm 100% GPU</div>
            <div class="potato-audio-hint">Click vào màn hình hoặc bấm Ctrl+Alt+M để mở lại hình</div>
        `;

        // Search Modal Overlay
        const searchModal = document.createElement("div");
        searchModal.id = "potato-search-modal";
        searchModal.innerHTML = `
            <input id="potato-search-input" type="text" placeholder="Tìm video hoặc dán link YouTube...">
            <button id="potato-search-submit">Tìm</button>
        `;

        document.documentElement.appendChild(hud);
        document.documentElement.appendChild(audioOverlay);
        document.documentElement.appendChild(searchModal);

        // Bind HUD events
        document.getElementById("btn-pin").addEventListener("click", () => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.toggle_pin();
            }
        });

        document.getElementById("btn-ghost").addEventListener("click", () => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.toggle_ghost();
            }
        });

        document.getElementById("btn-audio").addEventListener("click", () => {
            toggleAudioMode();
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.set_audio_mode(isAudioOnly);
            }
        });

        // Search modal toggle
        const searchInput = document.getElementById("potato-search-input");
        const searchBtn = document.getElementById("btn-search-toggle");
        searchBtn.addEventListener("click", () => {
            searchModal.classList.toggle("active");
            if (searchModal.classList.contains("active")) {
                setTimeout(() => searchInput.focus(), 50);
            }
        });

        function handleSearchSubmit() {
            const query = searchInput.value.trim();
            if (!query) return;
            searchModal.classList.remove("active");
            if (query.startsWith("http://") || query.startsWith("https://")) {
                if (window.pywebview && window.pywebview.api) {
                    window.pywebview.api.navigate_to(query);
                } else {
                    window.location.href = query;
                }
            } else {
                const searchUrl = "https://m.youtube.com/results?search_query=" + encodeURIComponent(query);
                window.location.href = searchUrl;
            }
        }

        document.getElementById("potato-search-submit").addEventListener("click", handleSearchSubmit);
        searchInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") handleSearchSubmit();
            if (e.key === "Escape") searchModal.classList.remove("active");
        });

        // Opacity slider
        const opacitySlider = document.getElementById("slider-opacity");
        opacitySlider.addEventListener("input", (e) => {
            const val = parseInt(e.target.value);
            document.getElementById("txt-opacity").innerText = val + "%";
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.set_opacity_direct(val);
            }
        });

        // Quality selection
        document.getElementById("sel-quality").addEventListener("change", (e) => {
            const val = e.target.value;
            currentResolution = val;
            enforceQuality(val);
            showToast("Độ phân giải: " + val.toUpperCase());
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.set_resolution(val);
            }
        });

        // Speed selection
        document.getElementById("sel-speed").addEventListener("change", (e) => {
            const rate = parseFloat(e.target.value);
            const video = document.querySelector("video");
            if (video) video.playbackRate = rate;
            showToast("Tốc độ phát: " + rate + "x");
        });

        document.getElementById("btn-home").addEventListener("click", () => {
            window.location.href = "https://m.youtube.com";
        });

        document.getElementById("btn-reload").addEventListener("click", () => {
            window.location.reload();
        });

        audioOverlay.addEventListener("click", () => {
            toggleAudioMode(false);
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.set_audio_mode(false);
            }
        });
    }

    // =========================================================================
    // 3. Audio-Only Screen Controller
    // =========================================================================
    function toggleAudioMode(forcedState) {
        if (typeof forcedState === "boolean") {
            isAudioOnly = forcedState;
        } else {
            isAudioOnly = !isAudioOnly;
        }

        const overlay = document.getElementById("potato-audio-overlay");
        const btn = document.getElementById("btn-audio");
        const videos = document.querySelectorAll("video");

        if (isAudioOnly) {
            if (overlay) overlay.classList.add("active");
            if (btn) btn.classList.add("active");
            videos.forEach(v => { v.style.opacity = "0.01"; });
            showToast("Đã bật Chế độ Audio Only (0% GPU)", ICONS.audio);
        } else {
            if (overlay) overlay.classList.remove("active");
            if (btn) btn.classList.remove("active");
            videos.forEach(v => { v.style.opacity = "1"; });
            showToast("Đã bật lại Video Player");
        }
    }

    // =========================================================================
    // 4. Ad-Blocker & Auto-Skip Engine
    // =========================================================================
    function runAdBlocker() {
        const skipSelectors = [
            ".ytp-ad-skip-button",
            ".ytp-ad-skip-button-modern",
            ".videoAdUiSkipButton",
            "button.ytp-ad-skip-button-modern",
            ".ytp-ad-preview-container"
        ];

        for (const selector of skipSelectors) {
            const btn = document.querySelector(selector);
            if (btn && typeof btn.click === "function") {
                btn.click();
            }
        }

        const player = document.querySelector(".html5-video-player");
        const video = document.querySelector("video");

        if (player && player.classList.contains("ad-showing") && video) {
            if (!isNaN(video.duration) && video.duration > 0) {
                video.currentTime = video.duration;
            }
            video.playbackRate = 16.0;
        }

        const adOverlays = document.querySelectorAll(
            ".ytp-ad-overlay-container, #player-ads, .ad-container, ytm-promoted-sparkles-web-renderer"
        );
        adOverlays.forEach(el => el.remove());
    }

    // =========================================================================
    // 5. Video Resolution Enforcer
    // =========================================================================
    function enforceQuality(quality) {
        const qualityMap = {
            "360p": "medium",
            "480p": "large",
            "720p": "hd720",
            "auto": "default"
        };
        const target = qualityMap[quality] || "large";
        const player = document.getElementById("movie_player");
        if (player) {
            try {
                if (typeof player.setPlaybackQualityRange === "function") {
                    player.setPlaybackQualityRange(target, target);
                }
                if (typeof player.setPlaybackQuality === "function") {
                    player.setPlaybackQuality(target);
                }
            } catch (e) {
                // Ignore silent player API errors
            }
        }
    }

    // =========================================================================
    // 6. Python Dispatch Callbacks & Feedback
    // =========================================================================
    window.potato_update_pin = function (pinned) {
        isPinned = pinned;
        const btn = document.getElementById("btn-pin");
        if (btn) {
            if (pinned) btn.classList.add("active");
            else btn.classList.remove("active");
        }
        showToast(pinned ? "Đã ghim cửa sổ trên cùng" : "Đã bỏ ghim cửa sổ", ICONS.pin);
    };

    window.potato_update_ghost = function (ghost) {
        isGhost = ghost;
        const btn = document.getElementById("btn-ghost");
        if (btn) {
            if (ghost) btn.classList.add("danger-active");
            else btn.classList.remove("danger-active");
        }
        showToast(ghost ? "Ghost Mode BẬT: Chuột xuyên qua video (Ctrl+Alt+G)" : "Ghost Mode TẮT: Tương tác bình thường", ICONS.ghost);
    };

    window.potato_update_opacity = function (percent) {
        currentOpacity = percent;
        const txt = document.getElementById("txt-opacity");
        const slider = document.getElementById("slider-opacity");
        if (txt) txt.innerText = percent + "%";
        if (slider) slider.value = percent;
        showToast("Độ trong suốt: " + percent + "%");
    };

    window.potato_update_audio = function (audioOnly) {
        toggleAudioMode(audioOnly);
    };

    // =========================================================================
    // 7. Lifecycle Initialization
    // =========================================================================
    function init() {
        createHUD();
        setInterval(runAdBlocker, 300);
        setInterval(() => {
            if (currentResolution !== "auto") {
                enforceQuality(currentResolution);
            }
        }, 3000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
