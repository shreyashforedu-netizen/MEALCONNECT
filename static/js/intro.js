document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("intro-video");
  const btn = document.getElementById("lets-go-btn");
  
  // Force play logic to ensure video never stops
  const forcePlay = () => {
    if (video.paused) {
      video.play().catch(e => {
        console.warn("Video playback blocked or failed:", e);
      });
    }
  };

  // Re-trigger play on any unintended pause
  video.addEventListener("pause", forcePlay);
  
  // Re-trigger play when tab becomes active again
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      forcePlay();
    }
  });

  // Handle missing/failed video by showing fallback
  video.addEventListener("error", () => {
    console.error("Video failed to load or play.");
    video.classList.add("error");
    const overlay = document.querySelector('.video-overlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
  });

  // Redirect to main home page
  btn.addEventListener("click", () => {
    // The video keeps playing naturally until the browser destroys the page
    window.location.href = "/home/";
  });
});
