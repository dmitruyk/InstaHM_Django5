export type UUID = string;

export type QType = "text" | "single" | "multiple" | "multi" | "numeric" | "image";


export interface Choice {
  id?: number;
  text: string;
  is_correct: boolean;
}

export interface Question {
  id: number;
  prompt: string;
  qtype: QType;
  category: number | null;
  difficulty: "easy" | "med" | "hard";
  text_answer?: string | null;
  numeric_answer?: number | null;
  image_required: boolean;
  choices?: Choice[];
}

export interface AttemptQuestion {
  id: number;
  question_id: number;
  prompt: string;
  qtype: QType;
  selected_choice_ids: number[];
  text_response?: string | null;
  numeric_response?: number | null;
  image?: string | null;
  is_correct: boolean;
  correct_choice_ids: number[];
  choices?: { id: number; text: string; is_correct: boolean }[]; // <— add this
}

export interface Attempt {
  id: number;
  player_uuid: UUID;
  created_at: string;
  score: number;
  total: number;
  attempt_questions: AttemptQuestion[];
}

export interface AttemptPayload {
  answers: {
    [attemptQuestionId: string]: {
      text_response?: string | null;
      numeric_response?: number | null;
      selected_choice_ids?: number[];
    }
  }
}

export interface QuestionPayload {
  prompt: string;
  qtype: QType;
  category?: number | null;
  difficulty: "easy" | "med" | "hard";
  text_answer?: string | null;
  numeric_answer?: number | null;
  image_required?: boolean;
  choices?: Choice[];
}
