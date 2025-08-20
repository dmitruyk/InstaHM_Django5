import { api } from "./client";
import { Attempt, AttemptPayload, Question, QuestionPayload } from "../types";

export async function startPlay(player_uuid: string) {
  const { data } = await api.post<Attempt>("/play/start/", { player_uuid });
  return data;
}

export async function submitPlay(attempt_id: number, answers: AttemptPayload["answers"], image?: File) {
  // multipart for optional image
  const form = new FormData();
  form.append("answers", new Blob([JSON.stringify({ answers })], { type: "application/json" }));
  if (image) form.append("image", image);
  const { data } = await api.post<Attempt>(`/play/submit/${attempt_id}/`, form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
}

export async function listAttempts(player_uuid: string) {
  const { data } = await api.get<Attempt[]>(`/attempts/`, { params: { player_uuid } });
  return data;
}

export async function getAttempt(id: number) {
  const { data } = await api.get<Attempt>(`/attempts/${id}/`);
  return data;
}

// Admin questions
export async function listQuestions() {
  const { data } = await api.get<Question[]>("/questions/");
  return data;
}

export async function createQuestion(payload: QuestionPayload) {
  const { data } = await api.post<Question>("/questions/", payload);
  return data;
}

export async function getQuestion(id: number) {
  const { data } = await api.get<Question>(`/questions/${id}/`);
  return data;
}

export async function updateQuestion(id: number, payload: QuestionPayload) {
  // use PUT to replace choices cleanly (serializer re-creates them)
  const { data } = await api.put<Question>(`/questions/${id}/`, payload);
  return data;
}

export async function deleteQuestion(id: number) {
  await api.delete(`/questions/${id}/`);
}
