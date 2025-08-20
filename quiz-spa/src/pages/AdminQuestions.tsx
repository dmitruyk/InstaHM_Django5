import { useEffect, useState } from "react";
import { createQuestion, listQuestions, updateQuestion, deleteQuestion, getQuestion } from "../api/quiz";
import { Question, QuestionPayload } from "../types";

type Mode = "create" | "edit";

const emptyForm: QuestionPayload = {
  prompt: "",
  qtype: "text",
  difficulty: "easy",
  category: null,
  text_answer: "",
  numeric_answer: null,
  image_required: false,
  choices: []
};

export default function AdminQuestions() {
  const [items, setItems] = useState<Question[]>([]);
  const [mode, setMode] = useState<Mode>("create");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<QuestionPayload>(emptyForm);
  const [loading, setLoading] = useState(false);

  const refresh = async () => setItems(await listQuestions());

  useEffect(() => {
    refresh();
  }, []);

  const resetForm = () => {
    setMode("create");
    setEditingId(null);
    setForm(emptyForm);
  };

  const startEdit = async (id: number) => {
    setLoading(true);
    try {
      const q = await getQuestion(id);
      setMode("edit");
      setEditingId(id);
      setForm({
        prompt: q.prompt,
        qtype: q.qtype as any,
        difficulty: q.difficulty as any,
        category: q.category ?? null,
        text_answer: q.text_answer ?? "",
        numeric_answer: q.numeric_answer ?? null,
        image_required: !!q.image_required,
        choices: q.choices || []
      });
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async () => {
    setLoading(true);
    try {
      if (mode === "create") {
        await createQuestion(form);
      } else if (mode === "edit" && editingId != null) {
        // IMPORTANT: send full choices array for single/multiple
        await updateQuestion(editingId, form);
      }
      await refresh();
      resetForm();
    } finally {
      setLoading(false);
    }
  };

  const onDelete = async (id: number) => {
    if (!confirm("Delete this question? This cannot be undone.")) return;
    setLoading(true);
    try {
      await deleteQuestion(id);
      await refresh();
      if (editingId === id) resetForm();
    } finally {
      setLoading(false);
    }
  };

  const addChoice = () => {
    setForm({ ...form, choices: [...(form.choices || []), { text: "", is_correct: false }] });
  };

  const updateChoice = (i: number, patch: Partial<{ text: string; is_correct: boolean }>) => {
    const choices = [...(form.choices || [])];
    choices[i] = { ...choices[i], ...patch };
    setForm({ ...form, choices });
  };

  const removeChoice = (i: number) => {
    const choices = [...(form.choices || [])];
    choices.splice(i, 1);
    setForm({ ...form, choices });
  };

  return (
    <div>
      <h2>Admin: Questions</h2>

      <div style={{ border: "1px solid #ddd", padding: 12, borderRadius: 8, marginBottom: 16 }}>
        <h3 style={{ marginTop: 0 }}>{mode === "create" ? "Create Question" : `Edit Question #${editingId}`}</h3>

        <label>Prompt<br/>
          <textarea
            value={form.prompt}
            onChange={(e) => setForm({ ...form, prompt: e.target.value })}
            rows={3}
            style={{ width: "100%" }}
          />
        </label>

        <div style={{ display: "flex", gap: 12, marginTop: 8, flexWrap: "wrap" }}>
          <label>Type&nbsp;
            <select
              value={form.qtype}
              onChange={(e) => setForm({ ...form, qtype: e.target.value as any, choices: e.target.value === "single" || e.target.value === "multiple" || e.target.value === "multi" ? (form.choices || []) : [] })}
            >
              <option value="text">text</option>
              <option value="numeric">numeric</option>
              <option value="single">single</option>
              <option value="multiple">multiple</option>
              <option value="multi">multi</option>
              <option value="image">image</option>
            </select>
          </label>

          <label>Difficulty&nbsp;
            <select value={form.difficulty} onChange={(e) => setForm({ ...form, difficulty: e.target.value as any })}>
              <option value="easy">easy</option>
              <option value="med">med</option>
              <option value="hard">hard</option>
            </select>
          </label>

          <label>
            Image required&nbsp;
            <input
              type="checkbox"
              checked={form.image_required}
              onChange={(e) => setForm({ ...form, image_required: e.target.checked })}
            />
          </label>
        </div>

        {/* Answers by type */}
        {form.qtype === "text" && (
          <div style={{ marginTop: 8 }}>
            <label>Text answer<br/>
              <input
                value={form.text_answer ?? ""}
                onChange={(e) => setForm({ ...form, text_answer: e.target.value })}
                style={{ width: 360 }}
              />
            </label>
          </div>
        )}

        {form.qtype === "numeric" && (
          <div style={{ marginTop: 8 }}>
            <label>Numeric answer<br/>
              <input
                type="number"
                value={form.numeric_answer ?? ""}
                onChange={(e) => setForm({ ...form, numeric_answer: e.target.value === "" ? null : Number(e.target.value) })}
                style={{ width: 160 }}
              />
            </label>
          </div>
        )}

        {(form.qtype === "single" || form.qtype === "multiple" || form.qtype === "multi") && (
          <div style={{ marginTop: 8 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <strong>Choices</strong>
              <button type="button" onClick={addChoice}>+ Add Choice</button>
            </div>
            {(form.choices || []).map((c, i) => (
              <div key={i} style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 6 }}>
                <input
                  placeholder="choice text"
                  value={c.text}
                  onChange={(e) => updateChoice(i, { text: e.target.value })}
                  style={{ width: 320 }}
                />
                <label>
                  correct{" "}
                  <input
                    type="checkbox"
                    checked={!!c.is_correct}
                    onChange={(e) => updateChoice(i, { is_correct: e.target.checked })}
                  />
                </label>
                <button type="button" onClick={() => removeChoice(i)}>🗑️</button>
              </div>
            ))}
            <p style={{ fontSize: 12, color: "#666", marginTop: 6 }}>
              For <em>single</em>, exactly one choice must be marked correct. For <em>multiple/multi</em>, at least one.
            </p>
          </div>
        )}

        <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
          <button disabled={loading} onClick={onSubmit}>
            {mode === "create" ? "Create" : "Save Changes"}
          </button>
          {mode === "edit" && (
            <button type="button" disabled={loading} onClick={resetForm}>Cancel</button>
          )}
        </div>
      </div>

      <h3>Existing</h3>
      <ul>
        {items.map((q) => (
          <li key={q.id} style={{ margin: "6px 0" }}>
            #{q.id} [{q.qtype}] {q.prompt.slice(0, 80)}
            <span style={{ marginLeft: 8 }}>
              <button onClick={() => startEdit(q.id)}>Edit</button>
              <button style={{ marginLeft: 6 }} onClick={() => onDelete(q.id)}>Delete</button>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
