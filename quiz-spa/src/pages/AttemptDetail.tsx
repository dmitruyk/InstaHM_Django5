import { useEffect, useState } from "react";
import { getAttempt } from "../api/quiz";
import { Attempt } from "../types";
import { useParams } from "react-router-dom";

export default function AttemptDetail() {
  const { id } = useParams();
  const [attempt, setAttempt] = useState<Attempt | null>(null);

  useEffect(() => {
    if (id) getAttempt(Number(id)).then(setAttempt);
  }, [id]);

  if (!attempt) return <div>Loading…</div>;

  return (
    <div>
      <h2>Attempt #{attempt.id}</h2>
      <p>Score: <strong>{attempt.score}</strong> / {attempt.total}</p>
      <div>
        {attempt.attempt_questions.map((aq) => (
          <div key={aq.id} style={{ border: "1px solid #eee", padding: 12, margin: "12px 0", borderRadius: 8 }}>
            <div style={{ fontWeight: 600 }}>{aq.prompt}</div>
            <div>Type: {aq.qtype}</div>
            <div>Your answer:
              {aq.qtype === "text" && <pre>{aq.text_response ?? "—"}</pre>}
              {aq.qtype === "numeric" && <pre>{aq.numeric_response ?? "—"}</pre>}
              {aq.qtype === "image" && (aq.image ? <div><img src={aq.image} style={{ maxWidth: 240 }} /></div> : "—")}
              {(aq.qtype === "single" || aq.qtype === "multiple") && (
                <pre>{JSON.stringify(aq.selected_choice_ids || [])}</pre>
              )}
            </div>
            <div>Result: {aq.is_correct ? "✅ Correct" : "❌ Incorrect"}</div>
            {(aq.qtype === "single" || aq.qtype === "multiple") && (
              <div>Correct choice IDs: <code>{JSON.stringify(aq.correct_choice_ids)}</code></div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
