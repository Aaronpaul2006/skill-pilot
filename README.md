# ✈️ SKILL PILOT — AI-Powered Adaptive Tutoring Platform

> An intelligent, gamified learning platform for college students that adapts to your unique learning style using Google Gemini 2.5 Flash AI.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1+-green?logo=flask)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange?logo=google)
![SQLite](https://img.shields.io/badge/DB-SQLite-lightgrey?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🚀 What is Skill Pilot?

Skill Pilot is a full-stack web application that provides **personalized AI tutoring** for college students. It detects your **VARK learning style** (Visual, Auditory, Reading, Kinesthetic) and **learning pace** (slow, medium, fast), then adapts every AI interaction accordingly — from chat explanations to document summaries to concept mind maps.

---

## ✨ Core Features

### 🤖 Adaptive AI Chat
- Real-time conversational tutoring powered by **Gemini 2.5 Flash**
- Responses adapt to student's VARK learning style and pace
- Subject-specific chat sessions with full history
- Pace detection engine that monitors response patterns

### 📄 PDF/Notes Upload & AI Explanation
- Upload **PDF, DOCX, or TXT** study materials
- AI extracts text and generates **adaptive explanations** tailored to learning style
- Dual-pane viewer: original text on the left, AI explanation on the right
- **Follow-up Q&A** — ask contextual questions about uploaded documents
- Document library with search and subject tagging

### 🗺️ Concept Mind Map Generator
- Enter any topic and AI generates a **15-25 node concept graph**
- **D3.js force-directed interactive visualization** with drag, pan, and zoom
- Click any node for **AI-generated concept notes** adapted to your style
- **Status tracking** — mark concepts as Understood / In Progress / Needs Review
- Nodes change color in real-time based on mastery status:
  - 🟢 Green = Understood | 🔵 Blue = In Progress | 🔴 Red = Needs Review | ⚪ Grey = Not Started
- **Learning Path mode** — shows recommended study order with numbered badges
- **PNG export** for offline study
- Maps saved per student with history and progress tracking

### 📅 Smart Study Planner
- AI generates personalized study plans based on exam dates and subjects
- Cram mode for last-minute preparation
- Session-by-session progress tracking
- Calendar-based daily task breakdown

### 🎮 Gamification System
- **XP & Leveling** — earn XP for every interaction (chat, uploads, maps, sessions)
- **6-tier rank system**: Scholar → Apprentice → Journeyman → Expert → Master → Sage
- **Daily/Weekly streaks** with longest streak tracking
- **Badge collection** — 12+ achievements across categories
- **Weekly leaderboard** with rankings
- **Daily & weekly challenges** with XP rewards
- Real-time toast notifications for XP gains and badge unlocks

### 🔐 Authentication & Onboarding
- Secure registration and login with bcrypt password hashing
- VARK learning style quiz during onboarding
- Learning pace self-assessment
- Subject focus selection

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.1+ |
| Database | SQLite + SQLAlchemy ORM |
| AI Engine | Google Gemini 2.5 Flash |
| Auth | Flask-Login + Flask-Bcrypt |
| Rate Limiting | Flask-Limiter |
| PDF Extraction | PyMuPDF (fitz) |
| DOCX Extraction | python-docx |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Visualization | D3.js 7.8 (CDN) |
| Export | dom-to-image (CDN) |
| Markdown | marked.js (CDN) |
| Fonts | Google Fonts (Syne + DM Sans) |

---

## 📁 Project Structure

```
skill-pilot/
├── app/
│   ├── __init__.py              # App factory, blueprint registration, DB init
│   ├── models.py                # All SQLAlchemy models (13 models)
│   ├── routes/
│   │   ├── auth.py              # Login, register, logout
│   │   ├── onboarding.py        # VARK quiz, pace assessment
│   │   ├── dashboard.py         # Main dashboard with stats
│   │   ├── chatbot.py           # AI chat with adaptive responses
│   │   ├── scheduler.py         # Smart study planner
│   │   ├── gamification.py      # XP, badges, leaderboard
│   │   ├── notes.py             # PDF/DOCX upload & AI explanation
│   │   ├── mindmap.py           # Concept mind map generator
│   │   └── test_routes.py       # Demo data setup
│   ├── services/
│   │   └── gamification.py      # XP engine, leveling, streaks, badges
│   ├── templates/
│   │   ├── auth/                # Login & register pages
│   │   ├── onboarding/          # VARK quiz templates
│   │   ├── dashboard/           # Main dashboard
│   │   ├── chatbot/             # AI chat interface
│   │   ├── scheduler/           # Study planner dashboard
│   │   ├── gamification/        # Hub, badges, leaderboard
│   │   ├── notes/               # Upload, view, history
│   │   ├── mindmap/             # Index, D3.js viewer, history
│   │   └── errors/              # 404, 429, 500 pages
│   └── static/
│       ├── css/                 # Stylesheets
│       └── js/                  # Client-side scripts
├── config.py                    # App configuration
├── run.py                       # Entry point
├── requirements.txt             # Python dependencies
└── .env                         # API keys (not committed)
```

---

## 📊 Database Models

| Model | Purpose |
|-------|---------|
| `User` | Core user account |
| `LearningProfile` | VARK style, pace, subject focus |
| `ChatMessage` | Chat history per user |
| `StudyPlan` | AI-generated study plans |
| `StudySession` | Individual study sessions |
| `PlayerProfile` | XP, level, streaks |
| `Badge` | Achievement definitions |
| `UserBadge` | Earned badges per user |
| `XPEvent` | XP transaction log |
| `Challenge` | Daily/weekly challenge definitions |
| `UserChallenge` | Challenge progress per user |
| `UploadedNote` | Uploaded documents with AI summaries |
| `MindMap` | Saved mind maps with JSON graph data |
| `ConceptStatus` | Per-concept mastery tracking |

---

## 🌐 API Routes

### Authentication
| Method | Route | Description |
|--------|-------|-------------|
| GET/POST | `/login` | User login |
| GET/POST | `/register` | User registration |
| GET | `/logout` | Logout |

### Dashboard
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/dashboard` | Main dashboard with stats widget |
| GET | `/dashboard/stats` | Detailed statistics |
| GET | `/dashboard/profile-edit` | Edit learning profile |

### AI Chat
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/chat` | Chat interface |
| POST | `/chat/send` | Send message to Gemini |

### Notes Upload
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/notes` | Upload page with recent notes |
| POST | `/notes/upload` | Upload & analyze document |
| GET | `/notes/view/<id>` | Dual-pane AI explanation viewer |
| POST | `/notes/ask/<id>` | Follow-up Q&A (AJAX) |
| GET | `/notes/history` | Document library |
| POST | `/notes/delete/<id>` | Delete a note |

### Mind Maps
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/mindmap` | Topic input + saved maps |
| POST | `/mindmap/generate` | Generate mind map via Gemini |
| GET | `/mindmap/view/<id>` | Interactive D3.js viewer |
| POST | `/mindmap/concept/notes` | AI notes for a concept (AJAX) |
| POST | `/mindmap/concept/status` | Update concept mastery (AJAX) |
| GET | `/mindmap/path/<id>` | Get learning path (AJAX) |
| GET | `/mindmap/history` | All saved mind maps |
| POST | `/mindmap/delete/<id>` | Delete a mind map |
| POST | `/mindmap/regenerate/<id>` | Regenerate with fresh AI data |

### Study Planner
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/scheduler` | Planner dashboard |
| POST | `/scheduler/generate` | Generate study plan |
| POST | `/scheduler/complete/<id>` | Mark session complete |

### Gamification
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/gamification` | Gamification hub |
| GET | `/gamification/badges` | Badge collection |
| GET | `/gamification/leaderboard` | Leaderboard |
| GET | `/gamification/api/stats` | Stats JSON |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/Aaronpaul2006/skill-pilot.git
cd skill-pilot

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the application
python run.py
```

The app will be available at **http://127.0.0.1:5000**

### Demo Account
Visit `/test/setup-demo` to create a demo account:
- **Email**: demo@skillpilot.com
- **Password**: demo123

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
```

---

## 🎨 UI Design

- **Theme**: Premium dark mode with deep navy/charcoal backgrounds
- **Primary Accent**: Purple gradient (#6c63ff → #a78bfa)
- **Typography**: Syne (headings) + DM Sans (body)
- **Design Language**: Glassmorphism cards, smooth micro-animations, gradient accents
- **Responsive**: Sidebar navigation with mobile hamburger menu

---

## 🗺️ Roadmap

- [x] Adaptive AI Chat with VARK detection
- [x] Smart Study Planner with AI scheduling
- [x] Full Gamification System (XP, badges, leaderboard)
- [x] PDF/Notes Upload with AI Explanation
- [x] Concept Mind Map Generator with D3.js
- [ ] Flashcard generator from uploaded notes
- [ ] Collaborative study rooms
- [ ] Mobile-responsive PWA
- [ ] Quiz generator with spaced repetition
- [ ] Integration with Google Calendar

---

## 👨‍💻 Author

**Aaron Paul** — [@Aaronpaul2006](https://github.com/Aaronpaul2006)

---

## 📄 License

This project is licensed under the MIT License.
