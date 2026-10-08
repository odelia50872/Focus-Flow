import * as ort from "onnxruntime-web";

const LANDMARK_COUNT = 478;
const WINDOW_FRAMES = 100;
let sessionPromise = null;

async function getSession() {
  if (!sessionPromise) {
    sessionPromise = ort.InferenceSession.create("/models/v4_2.onnx", {
      executionProviders: ["wasm"],
    });
  }
  return sessionPromise;
}

function clamp01(value) {
  return Math.max(0, Math.min(1, value));
}

function windowToTensor(frames) {
  const data = new Float32Array(WINDOW_FRAMES * LANDMARK_COUNT * 3);
  let offset = 0;
  for (const frame of frames) {
    for (let i = 0; i < LANDMARK_COUNT; i += 1) {
      const point = frame[i] || { x: 0, y: 0, z: 0 };
      data[offset] = point.x;
      data[offset + 1] = point.y;
      data[offset + 2] = point.z ?? 0;
      offset += 3;
    }
  }
  return data;
}

export async function inferFocusScore(frames) {
  if (!frames || frames.length < WINDOW_FRAMES) {
    return null;
  }
  const window = frames.slice(-WINDOW_FRAMES);
  try {
    const session = await getSession();
    const inputName = session.inputNames[0];
    const tensor = new ort.Tensor("float32", windowToTensor(window), [1, WINDOW_FRAMES, LANDMARK_COUNT, 3]);
    const results = await session.run({ [inputName]: tensor });
    const outputName = session.outputNames[0];
    const raw = Number(results[outputName].data[0] ?? 0.5);
    return {
      score: clamp01(raw),
      modelName: "v4_2",
      extractionType: "mediapipe_face_mesh",
    };
  } catch {
    const nose = window.map((frame) => frame[1]?.x ?? 0.5);
    const variance =
      nose.reduce((sum, x) => sum + (x - 0.5) ** 2, 0) / Math.max(nose.length, 1);
    const stillness = clamp01(1 - variance * 40);
    return {
      score: clamp01(0.45 + stillness * 0.4),
      modelName: "landmark_stillness_fallback",
      extractionType: "mediapipe_face_mesh",
    };
  }
}

export { WINDOW_FRAMES };
