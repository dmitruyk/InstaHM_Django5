import { useEffect, useRef, useMemo, useState } from "react";
import { startPlay, submitPlay } from "../api/quiz";
import { Attempt, AttemptPayload } from "../types";
import PlayerQuestion from "../components/PlayerQuestion";
import { useNavigate } from "react-router-dom";
import { usePlayer } from "../store/usePlayer";

export default function Play() {
  const ensure = usePlayer((s) => s.ensure);
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const startedRef = useRef(false);   // <— guard
  const [answers, setAnswers] = useState<AttemptPayload["answers"]>({});
  const [image, setImage] = useState<File | undefined>();
  const nav = useNavigate();

  useEffect(() => {
    if (startedRef.current) return;   // prevent duplicate call in StrictMode
    startedRef.current = true;

    const player_uuid = ensure();
    startPlay(player_uuid).then(setAttempt);
  }, [ensure]);

  const onPatch = (aqId: number, patch: any) => {
    setAnswers((prev) => ({ ...prev, [String(aqId)]: { ...prev[String(aqId)], ...patch } }));
    if (patch.image) setImage(patch.image);
  };

  const canSubmit = useMemo(() => !!attempt, [attempt]);

  const submit = async () => {
    if (!attempt) return;
    const res = await submitPlay(attempt.id, answers, image);
    nav(`/attempts/${res.id}`);
  };

  if (!attempt) return <div>Loading quiz…</div>;

  return (
    <div>
      <h2>Quiz</h2>
      <p>Answer the 5 questions below, then submit.</p>
      {attempt.attempt_questions.map((aq) => (
        <PlayerQuestion
          key={aq.id}
          aq={aq}
          value={answers[String(aq.id)]}
          onChange={(patch) => onPatch(aq.id, patch)}
        />
      ))}
      <button disabled={!canSubmit} onClick={submit}>Submit</button>
    </div>
  );
}
