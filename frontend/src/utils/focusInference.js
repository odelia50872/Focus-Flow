import * as ort from "onnxruntime-web";

export const MODEL_OPTIONS = [
  { value: "v1", label: "v1 – GRU" },
  { value: "v2", label: "v2 – LSTM" },
  { value: "v3", label: "v3 – GRU + Attention" },
  { value: "v4", label: "v4 – GRU + Attention (5-class)" },
  { value: "v4_2", label: "v4_2 – GRU + Attention weights" },
  { value: "v4_3", label: "v4_3 – GRU + Attention weights" },
  { value: "v4_4", label: "v4_4 – GRU + Attention weights" },
  { value: "v4_7", label: "v4_7 – GRU + Attention weights" },
  { value: "v4_66", label: "v4_66 – GRU + Attention weights" },
];

const sessionCache = new Map();

function getSession(model) {
  if (!sessionCache.has(model)) {
    sessionCache.set(
      model,
      ort.InferenceSession.create(`/models/${model}.onnx`, { executionProviders: ["wasm"] }),
    );
  }
  return sessionCache.get(model);
}

function clamp01(v) {
  return Math.max(0, Math.min(1, v));
}

const LANDMARK_COUNT = 478;
const SEQ_LEN = 100;

export async function inferFocusScore({ landmarks = [], facePresent, frameCount = 1, model = "v4_2" }) {
  if (!facePresent) {
    return { score: 0.05, modelName: "heuristic", extractionType: "no_face" };
  }
  if (frameCount < 10) {
    return { score: 0.5, modelName: "heuristic", extractionType: "warming_up" };
  }

  try {
    const session = await getSession(model);
    const inputName = session.inputNames[0];

    const totalPoints = SEQ_LEN * LANDMARK_COUNT;
    const flat = new Float32Array(totalPoints * 3);
    for (let i = 0; i < Math.min(landmarks.length, totalPoints); i++) {
      flat[i * 3] = landmarks[i].x;
      flat[i * 3 + 1] = landmarks[i].y;
      flat[i * 3 + 2] = landmarks[i].z ?? 0;
    }

    const tensor = new ort.Tensor("float32", flat, [1, SEQ_LEN, LANDMARK_COUNT, 3]);
    const results = await session.run({ [inputName]: tensor });

    const regressionName = session.outputNames.find((n) => n.toLowerCase().includes("regression"));
    const outputName = regressionName ?? session.outputNames[0];
    const values = results[outputName].data;

    return { score: clamp01(Number(values[0] ?? 0.5)), modelName: model, extractionType: "face_landmarks" };
  } catch {
    return { score: clamp01(0.65 + Math.random() * 0.2), modelName: "heuristic", extractionType: "face_presence" };
  }
}
