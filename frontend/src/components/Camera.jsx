import { useEffect, useRef, useState } from "react";
import { sampleFaceFromVideo } from "../utils/faceLandmarks";
import { WINDOW_FRAMES, inferFocusScore } from "../utils/focusInference";

const SAMPLE_HZ = 10;

export function Camera({ enabled, onScore, onFaceStatus }) {
  const videoRef = useRef(null);
  const framesRef = useRef([]);
  const [error, setError] = useState(null);
  const [liveScore, setLiveScore] = useState(null);
  const [faceStatus, setFaceStatus] = useState("waiting");
  const [bufferCount, setBufferCount] = useState(0);

  useEffect(() => {
    if (!enabled) return undefined;
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
        if (!cancelled) setError("Camera permission was denied. You can still watch without a focus score.");
      }
    }

    start();
    return () => {
      cancelled = true;
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return undefined;
    let cancelled = false;
    let timer = null;

    const tick = async () => {
      const video = videoRef.current;
      if (!video || cancelled) return;
      const sample = await sampleFaceFromVideo(video, performance.now());
      if (cancelled) return;
      if (!sample.facePresent) {
        setFaceStatus("missing");
        onFaceStatus?.("missing");
        framesRef.current = [];
        setBufferCount(0);
        return;
      }
      setFaceStatus("present");
      onFaceStatus?.("present");
      framesRef.current.push(sample.landmarks);
      if (framesRef.current.length > WINDOW_FRAMES) framesRef.current.shift();
      setBufferCount(framesRef.current.length);
      if (framesRef.current.length < WINDOW_FRAMES) return;
      const result = await inferFocusScore(framesRef.current);
      if (!result || cancelled) return;
      setLiveScore(result.score);
      onScore(result.score, result);
    };

    timer = window.setInterval(tick, 1000 / SAMPLE_HZ);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [enabled, onScore, onFaceStatus]);

  const secondsUntilScore = Math.max(0, Math.ceil((WINDOW_FRAMES - bufferCount) / SAMPLE_HZ));

  return (
    <aside className="camera-panel">
      <h2>Camera and focus score</h2>
      <p className="muted">
        The camera stays in this browser. We extract 478 MediaPipe face points at 10 frames per
        second, run the ONNX focus model on a 10-second window, and send only the numeric score to
        the server. Video is never uploaded.
      </p>
      <video ref={videoRef} muted playsInline className="camera-video" />
      {error && <p className="error">{error}</p>}
      {!error && faceStatus === "missing" && (
        <p className="warn" role="status">
          No face detected. Look at the camera. The model is not running until a face is visible.
        </p>
      )}
      {!error && faceStatus === "present" && liveScore === null && (
        <p className="muted">Collecting face landmarks… first score in about {secondsUntilScore} seconds.</p>
      )}
      <p className="camera-meta">
        Current focus score (0 = not focused, 1 = very focused):{" "}
        <strong>{liveScore === null ? "waiting" : liveScore.toFixed(2)}</strong>
      </p>
    </aside>
  );
}
