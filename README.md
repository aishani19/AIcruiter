<![CDATA[<div align="center">

# 🚀 AIcruiter

### AI-Powered Interview Preparation Platform

[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)

**Practice smarter. Interview better. Land the job.**

AIcruiter is an intelligent interview preparation platform that combines resume-based question generation, real-time AI feedback, speech analysis, and gamified progress tracking to simulate a realistic interview experience.

[Live Demo](#-deployment) · [Features](#-key-features) · [Tech Stack](#%EF%B8%8F-tech-stack) · [Getting Started](#-getting-started) · [API Reference](#-api-endpoints)

---

</div>

## ✨ Key Features

### 🎯 Resume-Grounded Question Generation
Upload your resume and get **personalized interview questions** tailored to your experience, skills, and target role. Questions are generated using a custom **RAG (Retrieval-Augmented Generation)** pipeline — not generic templates.

### 🧠 Retrieval-Augmented Generation (RAG) Pipeline
A custom-built RAG engine chunks your resume, scores relevance using TF-IDF + bigram matching, and feeds the most relevant excerpts to the LLM — ensuring every question and feedback is **grounded in your actual experience**.

### 🎤 Multi-Modal Answer Submission
Answer questions via **text, video, or audio**. Video/audio responses are transcribed using **Groq Whisper** and evaluated alongside text for a comprehensive analysis.

### 📊 AI-Powered Feedback & Scoring
Each answer is evaluated by an AI panel that provides:
- **Structured markdown feedback** with strengths, weaknesses, and suggestions
- **Resume alignment scoring** — how well your answer maps to your resume
- **STAR method analysis** — evaluates Situation, Task, Action, Result structure
- **Ideal points to cover** — what a perfect answer would include

### 💡 Real-Time AI Coaching
Get **instant live feedback** while drafting your answer — before final submission. Plus, request **AI-generated hints** grounded in your resume to guide your response.

### 📈 Performance Dashboard
Track your progress with interactive visualizations:
- **Circular progress** — overall interview readiness score
- **Bar charts** — historical session scores over time
- **Pie charts** — breakdown of eye contact, pacing, STAR alignment, and accuracy
- **AI-recommended goals** — personalized next steps

### 🏆 Leaderboard & Gamification
Compete with other users on a global leaderboard ranked by interview performance. Earn skill badges like **"Elite"** and **"Practitioner"**.

### 📜 Interview History & Session Replay
Review every past interview session with full question-answer-feedback detail. Deep-dive into individual sessions to track improvement.

### 🤝 Peer Match
Connect with other users for collaborative practice sessions.

---

## 🏗️ Architecture

```
┌──────────────────────────────────┐       ┌──────────────────────────────────┐
│         FRONTEND (Vercel)        │       │        BACKEND (Render)          │
│                                  │       │                                  │
│  React 18 + Vite + Tailwind CSS  │──────▶│  Flask + Gunicorn               │
│                                  │ /api  │                                  │
│  • About / Landing Page          │       │  • Auth (JWT + bcrypt)           │
│  • Login / Signup                │       │  • Resume PDF Parsing (PyPDF2)   │
│  • Get Started (Upload Resume)   │       │  • RAG Pipeline (resume_rag.py)  │
│  • Practice (Text/Video/Audio)   │       │  • Question Generation (Groq)    │
│  • AI Feedback Panel             │       │  • Audio Transcription (Whisper) │
│  • Dashboard (Recharts)          │       │  • Feedback Generation (Groq)    │
│  • Leaderboard                   │       │  • Speech/Video Analysis         │
│  • Interview History             │       │                                  │
│  • Peer Match                    │       │  PostgreSQL / SQLite             │
└──────────────────────────────────┘       └──────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| **React 18** | Component-based UI with lazy loading & error boundaries |
| **Vite 6** | Lightning-fast dev server and build tool |
| **Tailwind CSS 3.4** | Utility-first styling with custom dark theme |
| **React Router v7** | Client-side routing with SPA support |
| **Recharts** | Interactive bar charts, pie charts for dashboard |
| **react-circular-progressbar** | Animated score visualization |
| **react-media-recorder** | In-browser video/audio recording |
| **react-markdown** | Rendering AI feedback as formatted markdown |
| **Axios** | HTTP client with interceptors for auth |

### Backend
| Technology | Purpose |
|-----------|---------|
| **Flask** | Lightweight Python web framework |
| **Gunicorn** | Production WSGI server |
| **SQLAlchemy** | ORM for database models and queries |
| **PostgreSQL** | Production database (SQLite fallback) |
| **PyPDF2** | Resume PDF text extraction |
| **bcrypt** | Secure password hashing |
| **PyJWT** | JSON Web Token authentication |
| **Flask-CORS** | Cross-origin resource sharing |

### AI / ML
| Technology | Purpose |
|-----------|---------|
| **Groq API** (LLaMA 3.3 70B) | Question generation, feedback, hints, evaluation |
| **Groq Whisper** (whisper-large-v3) | Audio/video transcription |
| **Custom RAG Pipeline** | Resume chunking, TF-IDF scoring, context retrieval |
| **OpenCV** | Video frame analysis (eye contact detection) |
| **pydub + FFmpeg** | Audio extraction from video recordings |

### DevOps & Deployment
| Technology | Purpose |
|-----------|---------|
| **Docker** | Containerized local development environment |
| **Docker Compose** | Multi-service orchestration (backend + PostgreSQL) |
| **Render** | Backend API hosting (CI/CD from GitHub) |
| **Vercel** | Frontend static hosting (CI/CD from GitHub) |

---

## 📁 Project Structure

```
AIcruiter/
├── backend/
│   ├── app.py                 # Main Flask application (all API routes)
│   ├── models.py              # SQLAlchemy models (User, Session, Question, Response, Metrics)
│   ├── resume_rag.py          # Custom RAG pipeline (chunking, scoring, retrieval)
│   ├── groq_api.py            # Groq LLM integration (questions, feedback, hints)
│   ├── audio_transcription.py # Whisper transcription + video processing
│   ├── config.py              # App configuration
│   ├── init_db.py             # Database initialization script
│   ├── Dockerfile             # Backend Docker image
│   └── .env                   # Environment variables (not committed)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Route definitions with lazy loading
│   │   ├── components/
│   │   │   ├── AboutPage.jsx  # Landing page
│   │   │   ├── Login.jsx      # Auth (login/signup) with JWT
│   │   │   ├── GetStarted.jsx # Resume upload + question generation
│   │   │   ├── Practice.jsx   # Interview session (text/video/audio)
│   │   │   ├── Feedback.jsx   # AI evaluation results
│   │   │   ├── Dashboard.jsx  # Performance analytics
│   │   │   ├── Leaderboard.jsx# Global rankings
│   │   │   ├── History.jsx    # Past interview sessions
│   │   │   ├── SessionDetail.jsx # Individual session deep-dive
│   │   │   ├── PeerMatch.jsx  # Peer practice matching
│   │   │   └── Navbar.jsx     # Navigation bar
│   │   └── utils/
│   │       └── api.js         # Axios instance with auth interceptors
│   ├── vercel.json            # Vercel rewrite rules (API proxy)
│   ├── vite.config.js         # Vite config with dev proxy
│   └── package.json
│
├── Dockerfile                 # Root Docker image for docker-compose
├── docker-compose.yml         # Multi-service local dev (backend + PostgreSQL)
├── .dockerignore              # Docker build exclusions
├── render.yaml                # Render deployment configuration
├── requirements.txt           # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **PostgreSQL** (or use SQLite for quick testing)
- **Docker** (optional, for containerized setup)
- **Groq API Key** — [Get one free](https://console.groq.com)

---

### Option 1: Docker Setup (Recommended)

The fastest way to get the full stack running:

```bash
# 1. Clone the repository
git clone https://github.com/aishani19/AIcruiter.git
cd AIcruiter

# 2. Create a .env file at the project root
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "GEMINI_API_KEY=your_gemini_key_here" >> .env
echo "SECRET_KEY=your_secret_key_here" >> .env

# 3. Build and start all services
docker compose up --build
```

This starts:
- **Backend** → `http://localhost:5000`
- **PostgreSQL** → `localhost:5432`

Then run the frontend separately:
```bash
cd frontend
npm install
npm run dev
# Frontend → http://localhost:5173
```

---

### Option 2: Manual Setup

#### Backend

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
# Create backend/.env with:
DATABASE_URL=postgresql://user:password@localhost:5432/ai_interview_bot_db
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key

# 4. Start the backend
cd backend
python app.py
# Backend → http://localhost:5000
```

#### Frontend

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Start the dev server
npm run dev
# Frontend → http://localhost:5173
```

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/signup` | Register a new user |
| `POST` | `/api/login` | Login and receive JWT token |

### Interview Flow
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/generate-questions` | Upload resume → get AI questions | 🔒 |
| `POST` | `/api/submit-answer` | Submit answer (text/video/audio) → get feedback | 🔒 |
| `POST` | `/api/get-hint` | Get a resume-grounded hint for a question | 🔒 |
| `POST` | `/api/realtime-feedback` | Get live AI coaching on draft answer | 🔒 |

### Dashboard & Analytics
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/dashboard-stats` | Performance metrics, charts, goals | 🔒 |
| `GET` | `/api/history` | List all past interview sessions | 🔒 |
| `GET` | `/api/history/:sessionId` | Detailed session with Q&A + scores | 🔒 |
| `GET` | `/api/leaderboard` | Global user rankings | — |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/test` | API health check |
| `GET` | `/` | Backend status |

---

## 🗄️ Database Schema

```
┌──────────┐     ┌────────────────────┐     ┌─────────────┐
│  users   │────▶│ interview_sessions │────▶│  questions   │
│          │ 1:N │                    │ 1:N │              │
│ user_id  │     │ session_id         │     │ question_id  │
│ name     │     │ user_id (FK)       │     │ session_id   │
│ email    │     │ desired_occupation │     │ question_text│
│ password │     │ seniority_level    │     │ difficulty   │
│ resume   │     │ num_questions      │     │ order        │
└──────────┘     └────────────────────┘     └──────┬──────┘
                                                    │ 1:1
                                              ┌─────▼──────┐
                                              │  responses  │
                                              │             │
                                              │ response_id │
                                              │ answer_type │
                                              │ transcript  │
                                              │ feedback    │
                                              │ text_answer │
                                              └──────┬──────┘
                                                     │ 1:1
                                            ┌────────▼────────┐
                                            │evaluation_metrics│
                                            │                  │
                                            │ wpm              │
                                            │ eye_contact      │
                                            │ filler_words     │
                                            │ overall_score    │
                                            │ duration         │
                                            └──────────────────┘
```

---

## 🐳 Docker

The project is fully containerized for consistent development environments:

```bash
# Start backend + PostgreSQL
docker compose up --build

# Stop all services
docker compose down

# Reset database
docker compose down -v
```

| Container | Image | Port |
|-----------|-------|------|
| `backend` | Python 3.10 + Gunicorn | `5000` |
| `db` | PostgreSQL 16 Alpine | `5432` |

---

## 🌐 Deployment

| Service | Platform | Auto-Deploy |
|---------|----------|-------------|
| **Backend API** | [Render](https://render.com) | ✅ On push to `main` |
| **Frontend** | [Vercel](https://vercel.com) | ✅ On push to `main` |

The frontend proxies all `/api/*` requests to the Render backend via `vercel.json` rewrite rules. No CORS issues in production.

---

## 🔐 Environment Variables

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_interview_bot_db
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_jwt_secret_key
```

### Root (`.env` — for Docker Compose)
```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_jwt_secret_key
```

> ⚠️ **Never commit `.env` files.** They are excluded via `.gitignore`.

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ by [Aishani](https://github.com/aishani19)**

⭐ Star this repo if you found it useful!

</div>
]]>
