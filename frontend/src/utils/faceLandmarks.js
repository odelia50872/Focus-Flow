import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

const FRAME_BUFFER_SIZE = 100;
const frameBuffer = [];
let faceLandmarker = null;
let initPromise = null;

async function initMediaPipe() {
  if (faceLandmarker) return faceLandmarker;
  if (initPromise) return initPromise;

  initPromise = (async () => {
    const vision = await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.17/wasm",
    );
    faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath:
          "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        delegate: "GPU",
      },
      runningMode: "VIDEO",
      numFaces: 1,
      outputFaceBlendshapes: false,
    });
    return faceLandmarker;
  })();

  return initPromise;
}

export async function sampleFaceFromVideo(video) {
  if (!video.videoWidth || !video.videoHeight) {
    return { facePresent: false, landmarks: [], frameCount: 0 };
  }

  try {
    const landmarker = await initMediaPipe();
    const results = landmarker.detectForVideo(video, performance.now());

    if (!results.faceLandmarks || results.faceLandmarks.length === 0) {
      frameBuffer.length = 0;
      return { facePresent: false, landmarks: [], frameCount: 0 };
    }

    // MediaPipe returns 478 landmarks with x, y, z normalized 0-1
    const frameLandmarks = results.faceLandmarks[0].map((lm) => ({
      x: lm.x,
      y: lm.y,
      z: lm.z,
    }));

    frameBuffer.push(frameLandmarks);
    if (frameBuffer.length > FRAME_BUFFER_SIZE) frameBuffer.shift();

    const allLandmarks = frameBuffer.flatMap((f) => f);
    return { facePresent: true, landmarks: allLandmarks, frameCount: frameBuffer.length };
  } catch {
    // fallback if MediaPipe fails
    frameBuffer.length = 0;
    return { facePresent: false, landmarks: [], frameCount: 0 };
  }
}
