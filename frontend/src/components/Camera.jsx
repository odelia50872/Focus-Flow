import { useEffect, useRef, useState } from "react";
import { sampleFaceFromVideo } from "../utils/faceLandmarks";
import { inferFocusScore } from "../utils/focusInference";

export function Camera({ enabled, model, onScore, intervalMs = 10000 }) {
  const videoRef = useRef(null);
  const [camError, setCamError] = useState(null);
  const [liveScore, setLiveScore] = useState(null);
  const [facePresent, setFacePresent] = useState(null);

  useEffect(() => {
    if (!enabled) return;
    let stream = null;
    let cancelled = false;

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: 640, height: 480 },
          audio: false,
        });
        if (cancelled || !videoRef.current) return;
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      } catch {
        if (!cancelled) setCamError("Camera permission denied or unavailable.");
      }
    }

    start();
    return () => {
      cancelled = true;
      stream?.getTracks().forEach((t) => t.stop());
      if (videoRef.current) videoRef.current.srcObject = null;
    };
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;

    const tick = async () => {
      const video = videoRef.current;
      if (!video || cancelled) return;
      const sample = await sampleFaceFromVideo(video);
      setFacePresent(sample.facePresent);
      const result = await inferFocusScore({ ...sample, model });
      if (cancelled) return;
      setLiveScore(result.score);
      onScore(result.score, { modelName: result.modelName, extractionType: result.extractionType });
    };

    const id = window.setInterval(tick, intervalMs);
    tick();
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [enabled, model, intervalMs, onScore]);

  if (!enabled) {
    return (
      <div className="camera-panel">
        <p className="muted">Camera is off. Enable it to measure focus.</p>
      </div>
    );
  }

  return (
    <div className="camera-panel">
      <video ref={videoRef} muted playsInline className="camera-video" />
      {camError && <p className="error">{camError}</p>}
      {!camError && facePresent === false && (
        <p className="warn">⚠ No face detected — please face the camera.</p>
      )}
      {!camError && facePresent !== false && (
        <p className="camera-meta">
          Live focus: {liveScore === null ? "…" : `${Math.round(liveScore * 100)}%`}
        </p>
      )}
    </div>
  );
}
