import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

let landmarkerPromise = null;

async function getLandmarker() {
  if (!landmarkerPromise) {
    landmarkerPromise = (async () => {
      const vision = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.17/wasm",
      );
      return FaceLandmarker.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath:
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        },
        runningMode: "VIDEO",
        numFaces: 1,
        outputFaceBlendshapes: false,
        outputFacialTransformationMatrixes: false,
      });
    })();
  }
  return landmarkerPromise;
}

export async function sampleFaceFromVideo(video, timestampMs) {
  if (!video.videoWidth || !video.videoHeight) {
    return { facePresent: false, landmarks: [] };
  }
  try {
    const landmarker = await getLandmarker();
    const result = landmarker.detectForVideo(video, timestampMs);
    const face = result.faceLandmarks?.[0];
    if (!face || face.length < 478) {
      return { facePresent: false, landmarks: [] };
    }
    return {
      facePresent: true,
      landmarks: face.slice(0, 478).map((point) => ({ x: point.x, y: point.y, z: point.z ?? 0 })),
    };
  } catch {
    return { facePresent: false, landmarks: [] };
  }
}
