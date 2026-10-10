/**
 * PotatoYT-Mini - Client Engine Injection
 * Ultra-lightweight DOM manager, AdBlock & Auto-Skip, Quality Limiter,
 * and Bi-directional HUD Controls.
 */

(function () {
    console.log("[PotatoYT] Initializing Lightweight Engine...");

    let currentResolution = "480p";
    let isAudioOnly = false;
    let isPinned = true;
    let isGhost = false;

    // =========================================================================
    // 1. HUD Construction & Injection
    // =========================================================================
    function createHUD() {
        if (document.getElementById("potato-hud-container")) return;

        const hud = document.createElement("div");
        hud.id = "potato-hud-container";
        hud.innerHTML = `
            <div class="potato-hud-left">
                <span class="potato-title">🥔 PotatoYT</span>
                <button id="btn-pin" class="potato-btn active" title="Ghim trên cùng (Ctrl+Alt+T)">📌 Pin</button>
                <button id="btn-ghost" class="potato-btn" title="Chế độ xuyên thấu chuột (Ctrl+Alt+G)">👻 Ghost</button>
                <button id="btn-audio" class="potato-btn" title="Chỉ nghe nhạc, tắt màn hình giảm 100% GPU (Ctrl+Alt+M)">🎵 Audio</button>
            </div>
            <div class="potato-hud-right">
                <select id="sel-quality" class="potato-select" title="Khóa độ phân giải tiết kiệm CPU">
                    <option value="360p">360p (Siêu mượt)</option>
                    <option value="480p" selected>480p (Chuẩn PiP)</option>
                    <option value="720p">720p (HD)</option>
                    <option value="auto">Tự động</option>
                </select>
                <button id="btn-op-down" class="potato-btn" title="Giảm độ mờ (Ctrl+Alt+[)">-</button>
                <span id="txt-opacity" style="font-size:11px; color:#94a3b8; font-weight:600;">100%</span>
                <button id="btn-op-up" class="potato-btn" title="Tăng độ mờ (Ctrl+Alt+])">+</button>
                <select id="sel-size" class="potato-select" title="Kích thước cửa sổ nhanh">
                    <option value="custom" disabled selected>📏 Kích thước</option>
                    <option value="360x225">Nhỏ (360x225)</option>
                    <option value="480x300">Vừa (480x300)</option>
                    <option value="640x380">Lớn (640x380)</option>
                </select>
                <button id="btn-home" class="potato-btn" title="Trang chủ">🏠</button>
                <button id="btn-reload" class="potato-btn" title="Tải lại">🔄</button>
            </div>
        `;

        // Audio overlay
        const audioOverlay = document.createElement("div");
        audioOverlay.id = "potato-audio-overlay";
        audioOverlay.innerHTML = `
            <div class="potato-pulse">🎵</div>
            <div style="font-weight:700; color:#38bdf8; margin-bottom:4px;">Chế độ Tiết kiệm GPU (Audio Only)</div>
            <div>Âm thanh vẫn phát - GPU & CPU giảm tải tối đa</div>
            <div style="margin-top:8px; font-size:10px; color:#64748b;">Nhấn Ctrl+Alt+M hoặc nút Audio để mở lại hình</div>
        `;

        // Ghost hint banner
        const ghostBanner = document.createElement("div");
        ghostBanner.id = "potato-ghost-banner";
        ghostBanner.innerText = "👻 Ghost Mode BẬT: Bấm Ctrl+Alt+G để tắt xuyên thấu";

        document.documentElement.appendChild(hud);
        document.documentElement.appendChild(audioOverlay);
        document.documentElement.appendChild(ghostBanner);

        // Bind events
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

        document.getElementById("btn-op-down").addEventListener("click", () => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.adjust_opacity(-10);
            }
        });

        document.getElementById("btn-op-up").addEventListener("click", () => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.adjust_opacity(10);
            }
        });

        document.getElementById("sel-quality").addEventListener("change", (e) => {
            const val = e.target.value;
            currentResolution = val;
            enforceQuality(val);
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.set_resolution(val);
            }
        });

        document.getElementById("sel-size").addEventListener("change", (e) => {
            const val = e.target.value;
            if (val === "360x225") {
                if (window.pywebview && window.pywebview.api) window.pywebview.api.resize_preset(360, 225);
            } else if (val === "480x300") {
                if (window.pywebview && window.pywebview.api) window.pywebview.api.resize_preset(480, 300);
            } else if (val === "640x380") {
                if (window.pywebview && window.pywebview.api) window.pywebview.api.resize_preset(640, 380);
            }
            e.target.value = "custom";
        });

        document.getElementById("btn-home").addEventListener("click", () => {
            window.location.href = "https://m.youtube.com";
        });

        document.getElementById("btn-reload").addEventListener("click", () => {
            window.location.reload();
        });
    }

    // =========================================================================
    // 2. Audio-Only / Screen-Off Mode
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
            videos.forEach(v => {
                v.style.opacity = "0.01"; // Keep playing audio without rendering pixels
            });
        } else {
            if (overlay) overlay.classList.remove("active");
            if (btn) btn.classList.remove("active");
            videos.forEach(v => {
                v.style.opacity = "1";
            });
        }
    }

    // =========================================================================
    // 3. Ad-Blocker & Auto-Skipper Engine
    // =========================================================================
    function runAdBlocker() {
        // 1. Detect & click skip ad buttons instantly
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
                console.log("[PotatoYT] Clicked Ad Skip Button!");
            }
        }

        // 2. Handle in-video ads that can be fast-forwarded
        const player = document.querySelector(".html5-video-player");
        const video = document.querySelector("video");

        if (player && player.classList.contains("ad-showing") && video) {
            if (!isNaN(video.duration) && video.duration > 0) {
                video.currentTime = video.duration;
            }
            video.playbackRate = 16.0;
        }

        // 3. Remove overlay ads
        const adOverlays = document.querySelectorAll(
            ".ytp-ad-overlay-container, #player-ads, .ad-container, ytm-promoted-sparkles-web-renderer"
        );
        adOverlays.forEach(el => el.remove());
    }

    // =========================================================================
    // 4. Quality / Resolution Enforcer
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
    // 5. Global API for Python callbacks
    // =========================================================================
    window.potato_update_pin = function (pinned) {
        isPinned = pinned;
        const btn = document.getElementById("btn-pin");
        if (btn) {
            if (pinned) btn.classList.add("active");
            else btn.classList.remove("active");
        }
    };

    window.potato_update_ghost = function (ghost) {
        isGhost = ghost;
        const btn = document.getElementById("btn-ghost");
        const banner = document.getElementById("potato-ghost-banner");
        if (btn) {
            if (ghost) btn.classList.add("active");
            else btn.classList.remove("active");
        }
        if (banner) {
            banner.style.display = ghost ? "block" : "none";
        }
    };

    window.potato_update_opacity = function (percent) {
        const txt = document.getElementById("txt-opacity");
        if (txt) txt.innerText = percent + "%";
    };

    window.potato_update_audio = function (audioOnly) {
        toggleAudioMode(audioOnly);
    };

    // =========================================================================
    // 6. Loop & Lifecycle
    // =========================================================================
    function init() {
        createHUD();
        // Run AdBlock every 350ms
        setInterval(runAdBlocker, 350);
        // Periodic check for video quality every 3s
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
