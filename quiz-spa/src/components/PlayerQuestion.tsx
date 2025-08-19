import { AttemptQuestion } from "../types";

type Props = {
  aq: AttemptQuestion;
  value: any;
  onChange: (patch: any) => void;
};

export default function PlayerQuestion({ aq, value, onChange }: Props) {
  const v = value || {};
  const choices = aq.choices || [];

  const isSingle = aq.qtype === "single";
  const isMultiple = aq.qtype === "multiple" || aq.qtype === "multi"; // <-- fix

  const wrapperStyle: React.CSSProperties = {
    border: "1px solid #ddd",
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  };

  return (
    <div style={wrapperStyle}>
      <div style={{ fontWeight: 600, marginBottom: 8 }}>{aq.prompt}</div>

      {/* TEXT */}
      {aq.qtype === "text" && (
        <textarea
          value={v.text_response || ""}
          onChange={(e) => onChange({ text_response: e.target.value })}
          rows={3}
          style={{ width: "100%" }}
          aria-label="Text answer"
        />
      )}

      {/* NUMERIC */}
      {aq.qtype === "numeric" && (
        <input
          type="number"
          value={v.numeric_response ?? ""}
          onChange={(e) =>
            onChange({
              numeric_response: e.target.value === "" ? null : Number(e.target.value),
            })
          }
          aria-label="Numeric answer"
        />
      )}

      {/* SINGLE (radio) */}
      {isSingle && (
        <div role="radiogroup" aria-label="Single choice">
          {choices.length === 0 && (
            <p style={{ fontSize: 12, color: "#666" }}>No options defined.</p>
          )}
          {choices.map((c) => (
            <label key={c.id} style={{ display: "block", cursor: "pointer" }}>
              <input
                type="radio"
                name={`q-${aq.id}`}
                checked={(v.selected_choice_ids?.[0] ?? null) === c.id}
                onChange={() => onChange({ selected_choice_ids: [c.id] })}
              />{" "}
              {c.text}
            </label>
          ))}
        </div>
      )}

      {/* MULTIPLE (checkboxes) */}
      {isMultiple && (
        <div aria-label="Multiple choice">
          {choices.length === 0 && (
            <p style={{ fontSize: 12, color: "#666" }}>No options defined.</p>
          )}
          {choices.map((c) => {
            const selected: number[] = v.selected_choice_ids || [];
            const checked = selected.includes(c.id);
            return (
              <label key={c.id} style={{ display: "block", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={(e) => {
                    const next = e.target.checked
                      ? [...selected, c.id]
                      : selected.filter((id: number) => id !== c.id);
                    onChange({ selected_choice_ids: next });
                  }}
                />{" "}
                {c.text}
              </label>
            );
          })}
        </div>
      )}

      {/* IMAGE */}
      {aq.qtype === "image" && (
        <input
          type="file"
          accept="image/*"
          onChange={(e) => onChange({ image: e.target.files?.[0] })}
          aria-label="Image upload"
        />
      )}

      {/* Unknown qtype — small hint for debugging */}
      {!(isSingle || isMultiple || ["text", "numeric", "image"].includes(aq.qtype)) && (
        <p style={{ fontSize: 12, color: "#a00" }}>
          Unsupported question type: <code>{aq.qtype}</code>
        </p>
      )}
    </div>
  );
}
