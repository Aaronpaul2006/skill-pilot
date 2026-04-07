# ✈️ SKILL PILOT
### AI-Powered Adaptive Tutoring Platform for College Students

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-2.5--flash-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=flat-square)

> ✈️ "Your AI tutor that adapts to YOU — not the other way around."

---

## 📌 About

SKILL PILOT is an AI-powered web platform built for college students.
It acts as a 24/7 personal tutor that adapts its teaching style and
pace based on how each individual student learns — using the VARK
learning model and real-time behavioral signal detection.

Built as Micro Project - 02 | EdTech & AI | Industry Focus

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎨 VARK Detection | Detects Visual / Auditory / Reading / Kinesthetic style |
| ⚡ Pace Adaptation | Detects Slow / Medium / Fast learning pace |
| 🔄 Real-time Signals | Auto-adjusts pace based on chat behavior |
| 🧠 AI Chatbot | Powered by Google Gemini 2.5 Flash |
| 📅 Study Planner | AI-generated dynamic exam schedules |
| 🎮 Gamification | XP, streaks, badges, challenges, leaderboards |
| 📊 Dashboard | Personalized tips, topics, stats |
| 📈 Analytics | Per-subject learning breakdown |
| 🔒 Security | bcrypt, rate limiting, input sanitization |
| 📱 Responsive | Mobile-friendly dark UI |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Framework | Flask |
| Database | SQLite + SQLAlchemy |
| AI Engine | Google Gemini 2.5 Flash |
| Authentication | Flask-Login + Flask-Bcrypt |
| Security | Flask-Limiter |
| Frontend | HTML5 + CSS3 + JavaScript |
| Typography | Syne + DM Sans (Google Fonts) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Free Google Gemini API key from https://aistudio.google.com

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/Aaronpaul2006/skill-pilot.git
cd skill-pilot
```

#### 2. Create virtual environment
```bash
python -m venv venv
```

#### 3. Activate virtual environment
```bash
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

#### 4. Install all dependencies
```bash
pip install -r requirements.txt
```

#### 5. Setup environment variables
```bash
cp .env.example .env
```

Then open `.env` and fill in your values:
- `SECRET_KEY` — any random string
- `GEMINI_API_KEY` — get free key from [aistudio.google.com](https://aistudio.google.com)

#### 6. Run the application
```bash
python run.py
```

#### 7. Open in your browser
```
http://127.0.0.1:5000/test
```

---

## 🧪 Testing & Demo

| URL | Purpose |
|---|---|
| `/test` | Full test panel |
| `/health` | System health check |
| `/test/api-check` | Verify Gemini connection |
| `/test/setup-demo` | Load demo data |
| `/register` | Create new account |
| `/login` | Login page |
| `/dashboard` | Student dashboard |
| `/chat` | AI tutor chat |
| `/scheduler` | Smart Study Planner |
| `/gamification` | Gamification Hub & Leaderboard |

### Quick Demo Login
After visiting `/test/setup-demo`:
- **Email:** `demo@skillpilot.com`
- **Password:** `demo123`

---

## 📁 Project Structure

```
skill-pilot/
├── app/
│   ├── routes/
│   │   ├── auth.py          # Login, Register, Logout
│   │   ├── onboarding.py    # VARK quiz + pace detection
│   │   ├── dashboard.py     # Personalized dashboard
│   │   ├── chatbot.py       # Gemini AI chatbot
│   │   ├── scheduler.py     # Smart Study Planner
│   │   ├── gamification.py  # Gamification routes
│   │   └── test_routes.py   # Testing + demo routes
│   ├── services/
│   │   └── gamification.py  # Core gamification engine
│   ├── templates/
│   │   ├── auth/            # Login, Register, Profile
│   │   ├── onboarding/      # Quiz, Result
│   │   ├── dashboard/       # Dashboard, Stats, Edit
│   │   ├── chatbot/         # Chat interface
│   │   ├── scheduler/       # Study Planner + session view
│   │   ├── gamification/    # Gamification Hub, Badges, Leaderboard
│   │   └── errors/          # 404, 500, 429 pages
│   ├── __init__.py          # Flask app factory
│   └── models.py            # User, Profile, Chat, Gamification & Planner Models
├── config.py                # App configuration
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── .env.example             # Environment template
└── README.md                # This file
```

---

## 🗄️ Database Models

### User
- `id`, `name`, `email`, `password` (hashed), `created_at`

### LearningProfile
- `learning_style` (visual/auditory/reading/kinesthetic)
- `learning_pace` (slow/medium/fast)
- `subject_focus` (10 subjects)
- `slow_signals`, `fast_signals` (real-time detection)
- `onboarding_done` (boolean)

### ChatMessage
- `role` (user/assistant)
- `content`, `subject`, `timestamp`

### Smart Planner & Gamification
- `StudyPlan`, `StudySession` (Manages auto-generated study blocks)
- `PlayerProfile` (Tracks Level, XP, streaks, user progress)
- `Badge`, `UserBadge` (Unlockable achievements tracking)
- `Challenge`, `UserChallenge` (Daily & weekly assigned tracked goals)
- `XPEvent` (Audit log of all earned points)

---

## 🧠 How Adaptation Works

1. Student completes **10-question VARK onboarding quiz**
2. System detects `learning_style` and `learning_pace`
3. Every AI response uses a **custom system prompt**
   built from the student's profile (8 unique prompts)
4. During chat, keywords are monitored:
   - `"don't understand"`, `"confused"` → slow signal 🐢
   - `"got it"`, `"harder"`, `"skip"` → fast signal 🚀
5. Every 5 messages, pace is **recalculated automatically**
6. AI prompt updates in **real-time** based on new pace

---

## 🔒 Security Features

- Passwords hashed with **bcrypt**
- Rate limiting: **30 req/min** on chat, **10 req/min** on login
- Input sanitization with `html.escape()`
- **Email format validation** with regex
- **Login attempt limiting** (5 attempts max)
- **Security headers** on all responses
- **Session timeout** (30 minutes)

---

## 🗺️ Future Roadmap

- [x] Gamification (streaks, badges, leaderboard)
- [x] Study schedule generator
- [ ] Mobile app (React Native)
- [ ] Voice input for auditory learners
- [ ] PDF/notes upload and AI explanation
- [ ] Teacher dashboard for class monitoring
- [ ] Multilingual support (Tamil, Hindi, Telugu)
- [ ] Fine-tuned subject-specific AI models

---

## 👨‍💻 Author

Built by **Aaron Paul**  
Micro Project - 02 | EdTech & AI

---

## 📄 License

MIT License — free to use, modify and distribute.

---

## 🙏 Acknowledgements

- [Google Gemini API](https://aistudio.google.com) for AI capabilities
- [VARK Learning Model](https://vark-learn.com) by Neil Fleming
- Flask community and documentation
