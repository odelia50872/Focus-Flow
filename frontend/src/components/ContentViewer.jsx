import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";

export const ContentViewer = forwardRef(function ContentViewer({ youtubeId, title }, ref) {
  const iframeRef = useRef(null);
  const playerRef = useRef(null);

  useEffect(() => {
    function onYouTubeReady() {
      playerRef.current = new window.YT.Player(iframeRef.current, {
        events: {
          onReady: () => {},
        },
      });
    }

    if (window.YT && window.YT.Player) {
      onYouTubeReady();
    } else {
      window.onYouTubeIframeAPIReady = onYouTubeReady;
      if (!document.getElementById("yt-api-script")) {
        const script = document.createElement("script");
        script.id = "yt-api-script";
        script.src = "https://www.youtube.com/iframe_api";
        document.body.appendChild(script);
      }
    }
  }, [youtubeId]);

  useImperativeHandle(ref, () => ({
    rewind(seconds) {
      if (playerRef.current && playerRef.current.getCurrentTime) {
        const current = playerRef.current.getCurrentTime();
        playerRef.current.seekTo(Math.max(0, current - seconds), true);
      }
    },
  }));

  return (
    <div className="viewer">
      <h2>{title}</h2>
      <div className="viewer-frame">
        <iframe
          ref={iframeRef}
          title={title}
          src={`https://www.youtube.com/embed/${youtubeId}?rel=0&enablejsapi=1`}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    </div>
  );
});
