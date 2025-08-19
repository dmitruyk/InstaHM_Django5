# 📝 Quiz App (Django + React)

A full-stack quiz application built with **Django 5.2.5**, **Django REST Framework**, and **React (Vite + TypeScript)**.  
It allows admins to create/manage questions and players to take quizzes with auto-grading and attempt history.

---

## 🚀 Features

### Backend (Django + DRF)
- Question bank with categories, difficulty, and multiple types:
  - Text
  - Numeric
  - Single choice
  - Multiple choice
  - Image upload
- Validation rules per type (e.g., single choice requires exactly one correct answer).
- Randomized quiz attempts (default 5 questions).
- Auto-grading logic for all types.
- Player tracking via UUID (no login needed).
- Attempt history + detailed review of answers.
- Admin interface (Django admin + API endpoints).
- CORS enabled for React frontend.

### Frontend (React + Vite + TS)
- SPA with React Router.
- Pages:
  - **Play Quiz** — start a new attempt, answer questions, submit.
  - **My Attempts** — view attempt history for the current player.
  - **Attempt Detail** — review answers (✅/❌).
  - **Admin Questions** — simple CRUD UI for question bank.
- Local player identity stored in `localStorage`.
- Accessible inputs, responsive layout.

---

## 🛠 Tech Stack

- **Backend:** Python 3.11, Django 5.2.5, DRF, Pillow, psycopg2
- **Frontend:** React 18, Vite, TypeScript, Axios, Zustand, React Router
- **Lint/Format:** black, isort, flake8, mypy, ESLint, Prettier
- **Database:** PostgreSQL (or SQLite in dev)

---

## 📂 Project Structure

```plaintext
project-root/
├── manage.py
├── server/                # Django project
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── quiz/                  # Django app
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── api.py
│   └── management/commands/seed_questions.py
├── quiz-spa/              # React frontend
│   ├── src/
│   │   ├── api/quiz.ts
│   │   ├── components/PlayerQuestion.tsx
│   │   ├── pages/
│   │   ├── store/usePlayer.ts
│   │   └── types.ts
│   └── package.json
├── requirements.txt
├── Makefile
└── README.md
```


---

## ⚡ Getting Started

### 1. Clone & Setup
```bash
git clone <repo-url>
cd project-root
```

### 2. Backend Setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# migrate and seed data
python manage.py migrate
python manage.py seed_questions
python manage.py runserver
```
Backend runs at: http://localhost:8000

### 3. Frontend Setup
```bash
cd quiz-spa
npm install
npm run dev
```
Frontend runs at: http://localhost:5173

🔧 Useful Makefile Commands
```bash
make runserver      # start Django
make start-frontend # start React dev server
make migrate        # run migrations
make lint           # run all linters
make lint-fix       # auto-fix backend + frontend code style
```

🧪 Testing
Backend: use pytest or Django’s manage.py test
Frontend: add tests with Vitest + React Testing Library

📸 Demo Flow
Admin adds questions via Django Admin or /api/questions/.
Player clicks Play, system creates an Attempt with 5 random questions.
Player submits answers, backend auto-grades.
Player can review attempts and see correct answers.

🛡 License
MIT — use freely for learning or as a starter project.