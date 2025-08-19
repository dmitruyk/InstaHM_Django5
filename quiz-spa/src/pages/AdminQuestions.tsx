import { useEffect, useState } from "react";
import { createQuestion, listQuestions } from "../api/quiz";
import { Question, QuestionPayload } from "../types";

export default function AdminQuestions() {
  const [items, setItems] = useState<Question[]>([]);
  const [form, setForm] = useState<QuestionPayload>({
    prompt: "",
    qtype: "text",
    difficulty: "easy",
    category: null,
    text_answer: "",
    numeric_answer: null,
    image_required: false,
    choices: []
  });

  const refresh = async () => setItems(await listQuestions());
  useEffect(() => { refresh(); }, []);

  const submit = async () => {
    await createQuestion(form);
    setForm({ ...form, prompt: "" });
    await refresh();
  };

  return (
    <div>
      <h2>Admin: Questions</h2>

      <div style={{ border: "1px solid #ddd", padding: 12, borderRadius: 8, marginBottom: 16 }}>
        <h3>Create</h3>
        <label>Prompt<br/>
          <textarea value={form.prompt} onChange={e => setForm({ ...form, prompt: e.target.value })}/>
        </label>
        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <label>Type&nbsp;
            <select value={form.qtype} onChange={e => setForm({ ...form, qtype: e.target.value as any })}>
              <option value="text">text</option>
              <option value="numeric">numeric</option>
              <option value="single">single</option>
              <option value="multiple">multiple</option>
              <option value="image">image</option>
            </select>
          </label>
          <label>Difficulty&nbsp;
            <select value={form.difficulty} onChange={e => setForm({ ...form, difficulty: e.target.value as any })}>
              <option value="easy">easy</option>
              <option value="med">med</option>
              <option value="hard">hard</option>
            </select>
          </label>
          <label>
            Image required&nbsp;
            <input type="checkbox" checked={form.image_required} onChange={e => setForm({ ...form, image_required: e.target.checked })}/>
          </label>
        </div>

        {form.qtype === "text" && (
          <div style={{ marginTop: 8 }}>
            <label>Text answer<br/>
              <input value={form.text_answer ?? ""} onChange={e => setForm({ ...form, text_answer: e.target.value })}/>
            </label>
          </div>
        )}

        {form.qtype === "numeric" && (
          <div style={{ marginTop: 8 }}>
            <label>Numeric answer<br/>
              <input type="number" value={form.numeric_answer ?? ""} onChange={e => setForm({ ...form, numeric_answer: e.target.value === "" ? null : Number(e.target.value) })}/>
            </label>
          </div>
        )}

        {(form.qtype === "single" || form.qtype === "multiple") && (
          <div style={{ marginTop: 8 }}>
            <strong>Choices</strong>
            <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
              <button onClick={() => setForm({ ...form, choices: [...(form.choices || []), { text: "", is_correct: false }] })}>
                + Add Choice
              </button>
            </div>
            {(form.choices || []).map((c, i) => (
              <div key={i} style={{ display: "flex", gap: 8, marginTop: 4 }}>
                <input
                  placeholder="text"
                  value={c.text}
                  onChange={e => {
                    const choices = [...(form.choices || [])];
                    choices[i] = { ...choices[i], text: e.target.value };
                    setForm({ ...form, choices });
                  }}
                />
                <label>
                  correct <input
                    type="checkbox"
                    checked={!!c.is_correct}
                    onChange={e => {
                      const choices = [...(form.choices || [])];
                      choices[i] = { ...choices[i], is_correct: e.target.checked };
                      setForm({ ...form, choices });
                    }}
                  />
                </label>
              </div>
            ))}
          </div>
        )}

        <div style={{ marginTop: 12 }}>
          <button onClick={submit}>Create Question</button>
        </div>
      </div>

      <h3>Existing</h3>
      <ul>
        {items.map(q => (
          <li key={q.id}>
            #{q.id} [{q.qtype}] {q.prompt.slice(0, 80)}
          </li>
        ))}
      </ul>
    </div>
  );
}
