import { useEffect, useState } from "react";
import { listAttempts } from "../api/quiz";
import { Attempt } from "../types";
import { Link } from "react-router-dom";
import { usePlayer } from "../store/usePlayer";

export default function Attempts() {
  const ensure = usePlayer((s) => s.ensure);
  const [items, setItems] = useState<Attempt[]>([]);

  useEffect(() => {
    const player_uuid = ensure();
    listAttempts(player_uuid).then(setItems);
  }, [ensure]);

  return (
    <div>
      <h2>My Attempts</h2>
      {items.length === 0 && <div>No attempts yet.</div>}
      <ul>
        {items.map((a) => (
          <li key={a.id}>
            <Link to={`/attempts/${a.id}`}>Attempt #{a.id}</Link> — {a.score}/{a.total} on {new Date(a.created_at).toLocaleString()}
          </li>
        ))}
      </ul>
    </div>
  );
}
