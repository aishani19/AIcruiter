<div align="center">

# 🚀 AIcruiter

### AI-Powered Interview Preparation Platform

**Practice smarter. Interview better. Land the job.**

<br/>

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-F55036?style=for-the-badge&logo=groq&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white)

<br/>

AIcruiter is an intelligent interview preparation platform that combines resume-based question generation, real-time AI feedback, speech analysis, and gamified progress tracking to simulate a realistic interview experience.

</div>

---

## 📑 Table of Contents

1. [Key Features](#1--key-features)
2. [Architecture](#2--architecture)
3. [Tech Stack](#3-%EF%B8%8F-tech-stack)
4. [Project Structure](#4--project-structure)
5. [Getting Started](#5--getting-started)
6. [API Reference](#6--api-reference)
7. [Database Schema](#7-%EF%B8%8F-database-schema)
8. [Docker](#8--docker)
9. [Deployment](#9--deployment)
10. [Environment Variables](#10--environment-variables)
11. [Contributing](#11--contributing)
12. [License](#12--license)

---

## 1. ✨ Key Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **🎯 Resume-Grounded Questions** | Upload your resume → get personalized interview questions tailored to your experience, skills, and target role using a custom RAG pipeline |
| 2 | **🧠 RAG Pipeline** | Custom-built engine that chunks your resume, scores relevance via TF-IDF + bigram matching, and feeds top excerpts to the LLM |
| 3 | **🎤 Multi-Modal Answers** | Answer via **text**, **video**, or **audio** — video/audio is transcribed using Groq Whisper for comprehensive evaluation |
| 4 | **📊 AI Feedback & Scoring** | Structured markdown feedback with strengths, weaknesses, STAR method analysis, resume alignment, and ideal answer points |
| 5 | **💡 Real-Time AI Coaching** | Get instant live feedback while drafting + resume-grounded hints before final submission |
| 6 | **📈 Performance Dashboard** | Interactive charts (bar, pie, circular progress) tracking scores, eye contact, pacing, and AI-recommended goals |
| 7 | **🏆 Leaderboard** | Global rankings by interview performance with skill badges ("Elite", "Practitioner") |
| 8 | **📜 Interview History** | Review every past session with full question → answer → feedback → score detail |
| 9 | **🤝 Peer Match** | Connect with other users for collaborative practice sessions |

---

## 2. 🏗 Architecture

```
┌─────────────────────────────────────┐        ┌──────────────────────────────────────┐
│          FRONTEND (Vercel)          │        │           BACKEND (Render)            │
│                                     │        │                                      │
│   React 18  ·  Vite  ·  Tailwind   │───────▶│   Flask  ·  Gunicorn  ·  SQLAlchemy  │
│                                     │  /api  │                                      │
│   Pages:                            │        │   Core Modules:                      │
│   ├── Landing / About               │        │   ├── app.py          (API routes)   │
│   ├── Login / Signup                │        │   ├── resume_rag.py   (RAG engine)   │
│   ├── Get Started (Resume Upload)   │        │   ├── groq_api.py     (LLM calls)    │
│   ├── Practice (Text/Video/Audio)   │        │   ├── audio_transcription.py         │
│   ├── Dashboard (Charts)            │        │   └── models.py       (DB schemas)   │
│   ├── Leaderboard                   │        │                                      │
│   ├── History / Session Detail      │        │   Database:                          │
│   └── Peer Match                    │        │   └── PostgreSQL / SQLite            │
└─────────────────────────────────────┘        └──────────────────────────────────────┘
```

---

## 3. 🛠️ Tech Stack

### Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18 | Component-based UI with lazy loading & error boundaries |
| Vite | 6 | Dev server and production build tool |
| Tailwind CSS | 3.4 | Utility-first styling with dark theme |
| React Router | 7 | Client-side SPA routing |
| Recharts | 2.15 | Bar charts, pie charts for dashboard |
| react-circular-progressbar | 2.1 | Animated score visualization |
| react-media-recorder | 1.7 | In-browser video/audio recording |
| react-markdown | 10.1 | Rendering AI feedback as formatted markdown |
| Axios | 1.7 | HTTP client with JWT interceptors |

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Flask | 2.x | Python web framework |
| Gunicorn | 23.0 | Production WSGI server |
| SQLAlchemy | — | ORM for database models and queries |
| PostgreSQL | 16 | Production database (SQLite fallback) |
| PyPDF2 | — | Resume PDF text extraction |
| bcrypt | — | Secure password hashing |
| PyJWT | — | JSON Web Token authentication |
| Flask-CORS | — | Cross-origin resource sharing |
| Flask-SocketIO | — | Real-time WebSocket support |

### AI / ML

| Technology | Model | Purpose |
|-----------|-------|---------|
| Groq API | LLaMA 3.3 70B | Question generation, feedback, hints, evaluation |
| Groq Whisper | whisper-large-v3 | Audio/video speech-to-text transcription |
| Custom RAG | — | Resume chunking → TF-IDF scoring → context retrieval |
| OpenCV | — | Video frame analysis (eye contact detection) |
| pydub + FFmpeg | — | Audio extraction from video recordings |

### DevOps

| Technology | Purpose |
|-----------|---------|
| Docker + Docker Compose | Containerized local dev (backend + PostgreSQL) |
| Render | Backend API hosting with CI/CD |
| Vercel | Frontend static hosting with CI/CD |
| GitHub | Source control + auto-deploy triggers |

---

## 4. 📁 Project Structure

```
AIcruiter/
│
├── 📂 backend/
│   ├── app.py                  # Flask app — all API routes
│   ├── models.py               # SQLAlchemy models (5 tables)
│   ├── resume_rag.py           # Custom RAG pipeline
│   ├── groq_api.py             # Groq LLM integration
│   ├── audio_transcription.py  # Whisper transcription + video processing
│   ├── config.py               # App configuration
│   ├── init_db.py              # Database initialization
│   ├── Dockerfile              # Backend container image
│   └── .env                    # Secrets (not committed)
│
├── 📂 frontend/
│   ├── 📂 src/
│   │   ├── App.jsx             # Route definitions + lazy loading
│   │   ├── 📂 components/
│   │   │   ├── AboutPage.jsx   # Landing page
│   │   │   ├── Login.jsx       # Auth (login / signup)
│   │   │   ├── GetStarted.jsx  # Resume upload → question generation
│   │   │   ├── Practice.jsx    # Interview session (text/video/audio)
│   │   │   ├── Feedback.jsx    # AI evaluation results
│   │   │   ├── Dashboard.jsx   # Performance analytics + charts
│   │   │   ├── Leaderboard.jsx # Global rankings
│   │   │   ├── History.jsx     # Past interview sessions
│   │   │   ├── SessionDetail.jsx # Session deep-dive
│   │   │   ├── PeerMatch.jsx   # Peer practice matching
│   │   │   └── Navbar.jsx      # Navigation bar
│   │   └── 📂 utils/
│   │       └── api.js          # Axios instance + auth interceptors
│   ├── vercel.json             # API proxy rewrite rules
│   ├── vite.config.js          # Dev server proxy config
│   └── package.json            # Frontend dependencies
│
├── Dockerfile                  # Root image for docker-compose
├── docker-compose.yml          # Backend + PostgreSQL orchestration
├── .dockerignore               # Build context exclusions
├── render.yaml                 # Render deployment config
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 5. 🚀 Getting Started

### Prerequisites

| Requirement | Version |
|------------|---------|
| Node.js | ≥ 18 |
| Python | ≥ 3.10 |
| PostgreSQL | Any (or use SQLite) |
| Docker | Optional |
| Groq API Key | [Get free key →](https://console.groq.com) |

---

### 5a. Docker Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/aishani19/AIcruiter.git
cd AIcruiter

# Create root .env
echo GROQ_API_KEY=your_key_here > .env
echo GEMINI_API_KEY=your_key_here >> .env
echo SECRET_KEY=your_secret_here >> .env

# Start backend + database
docker compose up --build

# In a separate terminal — start frontend
cd frontend
npm install
npm run dev
```

| Service | URL |
|---------|-----|
| Backend | `http://localhost:5000` |
| Frontend | `http://localhost:5173` |
| PostgreSQL | `localhost:5432` |

---

### 5b. Manual Setup

<details>
<summary><strong>Backend</strong></summary>

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_interview_bot_db
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_jwt_secret

# Run
cd backend
python app.py
# → http://localhost:5000
```

</details>

<details>
<summary><strong>Frontend</strong></summary>

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

</details>

---

## 6. 📡 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/signup` | Register new user |
| `POST` | `/api/login` | Login → JWT token |

### Interview Flow — 🔒 Auth Required

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate-questions` | Upload resume → AI-generated questions |
| `POST` | `/api/submit-answer` | Submit text/video/audio → AI feedback |
| `POST` | `/api/get-hint` | Get resume-grounded hint |
| `POST` | `/api/realtime-feedback` | Live AI coaching on draft answer |

### Analytics — 🔒 Auth Required

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard-stats` | Performance metrics + charts |
| `GET` | `/api/history` | All past interview sessions |
| `GET` | `/api/history/:sessionId` | Session detail (Q&A + scores) |

### Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/leaderboard` | Global user rankings |
| `GET` | `/api/test` | Health check |

---

## 7. 🗄️ Database Schema

```
users                    interview_sessions         questions
┌──────────────────┐     ┌──────────────────────┐   ┌──────────────────┐
│ user_id (PK)     │──┐  │ session_id (PK)      │──┐│ question_id (PK) │
│ name             │  └─▶│ user_id (FK)         │  └│ session_id (FK)  │
│ email (unique)   │     │ desired_occupation   │   │ question_text    │
│ password (hash)  │     │ seniority_level      │   │ difficulty       │
│ resume_path      │     │ num_questions        │   │ order            │
│ total_score      │     │ created_at           │   └────────┬─────────┘
│ created_at       │     └──────────────────────┘            │ 1:1
└──────────────────┘                                         ▼
                                                   responses
                                                   ┌──────────────────┐
                                                   │ response_id (PK) │
                                                   │ question_id (FK) │
                                                   │ answer_type      │
                                                   │ text_answer      │
                                                   │ transcript       │
                                                   │ feedback         │
                                                   │ video_path       │
                                                   │ audio_path       │
                                                   │ created_at       │
                                                   └────────┬─────────┘
                                                            │ 1:1
                                                            ▼
                                                   evaluation_metrics
                                                   ┌──────────────────┐
                                                   │ metric_id (PK)   │
                                                   │ response_id (FK) │
                                                   │ wpm              │
                                                   │ eye_contact      │
                                                   │ filler_words     │
                                                   │ avg_sentence_len │
                                                   │ duration         │
                                                   │ overall_score    │
                                                   └──────────────────┘
```

**Relationships:** `User` → 1:N → `InterviewSession` → 1:N → `Question` → 1:1 → `Response` → 1:1 → `EvaluationMetrics`

---

## 8. 🐳 Docker

```bash
docker compose up --build    # Start backend + PostgreSQL
docker compose down          # Stop all services
docker compose down -v       # Stop + wipe database
```

| Container | Image | Port |
|-----------|-------|------|
| `backend` | Python 3.10 + Gunicorn | `5000` |
| `db` | PostgreSQL 16 Alpine | `5432` |

---

## 9. 🌐 Deployment

| Service | Platform | Trigger | URL |
|---------|----------|---------|-----|
| Backend API | Render | Push to `main` | `aicruiter-api.onrender.com` |
| Frontend | Vercel | Push to `main` | Your Vercel domain |

> The frontend proxies `/api/*` requests to the Render backend via `vercel.json` rewrite rules — zero CORS issues in production.

---

## 10. 🔐 Environment Variables

### `backend/.env`

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `GROQ_API_KEY` | ✅ | Groq API key for LLM + Whisper |
| `SECRET_KEY` | ✅ | JWT signing secret |

### Root `.env` (Docker Compose)

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ | Passed to backend container |
| `GEMINI_API_KEY` | ❌ | Optional Gemini integration |
| `SECRET_KEY` | ✅ | JWT signing secret |

> ⚠️ **Never commit `.env` files.** They are excluded via `.gitignore`.

---

## 11. 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch — `git checkout -b feature/amazing-feature`
3. **Commit** your changes — `git commit -m "Add amazing feature"`
4. **Push** to the branch — `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 12. 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ by [Aishani](https://github.com/aishani19)**

⭐ **Star this repo if you found it useful!**

</div>
