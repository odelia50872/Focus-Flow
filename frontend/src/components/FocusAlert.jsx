import { useState } from "react";

const QUESTIONS = [
  "מה היה הנושא האחרון שהוסבר בסרטון?",
  "האם אתה יכול לסכם במשפט אחד מה למדת עכשיו?",
  "נסה להסביר את הרעיון האחרון במילים שלך.",
  "מה עוד לא הבנת? כדאי לחזור אחורה.",
];

export function FocusAlert({ score, onDismiss, onRewind }) {
  const [answered, setAnswered] = useState(false);
  const question = QUESTIONS[Math.floor(Math.random() * QUESTIONS.length)];

  if (score === null || score >= 0.4) return null;

  return (
    <div className="focus-alert">
      <div className="focus-alert-inner">
        <p className="focus-alert-title">⚠ הקשב שלך ירד</p>
        <p className="focus-alert-score">ציון נוכחי: {Math.round(score * 100)}%</p>
        {!answered ? (
          <>
            <p className="focus-alert-question">{question}</p>
            <div className="focus-alert-actions">
              <button type="button" onClick={() => setAnswered(true)}>
                הבנתי, אמשיך
              </button>
              <button type="button" className="secondary" onClick={onRewind}>
                חזור 30 שניות אחורה
              </button>
            </div>
          </>
        ) : (
          <div className="focus-alert-actions">
            <button type="button" onClick={onDismiss}>
              סגור
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
