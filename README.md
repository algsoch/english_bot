# AI Speaking Partner - Advanced English Learning Platform

🎯 **Free, Advanced, AI-Powered English Speaking Practice**

Practice English conversation with an AI tutor powered by Ollama (local, 100% free). Perfect for improving speaking skills, grammar, vocabulary, and pronunciation.

## ✨ Features

- 🎤 **Voice Recognition** - Real-time speech-to-text using Web Speech API
- 🔊 **Text-to-Speech** - Natural AI voice responses
- 💬 **Multiple Conversation Modes**:
  - Free Talk
  - Grammar Focus
  - Vocabulary Building
  - Pronunciation Practice
  - Business English
  - Travel English
- 📊 **Progress Tracking** - Track your learning journey
- 🎯 **AI Feedback** - Real-time corrections and suggestions
- 📱 **Mobile Optimized** - PWA support for mobile devices
- 🌐 **Share Online** - Can be deployed and shared

## 🛠️ Tech Stack

**Backend:**
- FastAPI (async Python web framework)
- Ollama (local AI - llama3.1:8b)
- PostgreSQL (database)
- WebSocket (real-time communication)

**Frontend:**
- React + Vite
- TailwindCSS (styling)
- Framer Motion (animations)
- Web Speech API (voice)

## 📋 Prerequisites

1. **PostgreSQL** - Already installed ✅
2. **Ollama** - Already installed with llama3.1:8b ✅
3. **Python 3.8+**
4. **Node.js 18+**

## 🚀 Quick Start

### 1. Setup Database

```bash
# Create database
createdb englishbot

# Import schema
psql -d englishbot -f database/schema.sql
```

### 2. Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your settings (already configured for local use)
```

### 3. Install & Run Backend

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start backend server
python -m backend.main
```

Backend will run on: http://localhost:8000

**Note:** Keep the virtual environment activated while running the backend.

### 4. Install & Run Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on: http://localhost:5173

## 📖 Usage

1. Open http://localhost:5173
2. Enter your name, email, and English level
3. Choose a conversation mode
4. Click "Start Speaking Practice"
5. **Hold the microphone button** to speak
6. AI will respond via voice automatically
7. Get instant feedback on grammar, vocabulary, or pronunciation

## 🎮 Conversation Modes

| Mode | Description |
|------|-------------|
| **Free Talk** | Natural, flowing conversation with follow-up questions |
| **Grammar Focus** | Specific grammar corrections with explanations |
| **Vocabulary** | Learn new words and alternative expressions |
| **Pronunciation** | Practice difficult words with phonetic guidance |
| **Business English** | Professional scenarios (meetings, presentations) |
| **Travel English** | Travel situations (airports, hotels, directions) |

## 📱 Mobile Support

The app is a Progressive Web App (PWA):

1. Open on mobile browser
2. Click "Add to Home Screen"
3. Use like a native app
4. Works offline (basic features)

## 🌐 Deploy Online (Free Options)

### Backend Options:
- **Railway** (Free tier)
- **Render** (Free tier)
- **Fly.io** (Free tier)

### Frontend Options:
- **Vercel** (Free, unlimited)
- **Netlify** (Free tier)
- **GitHub Pages** (Free)

### Database:
- **Supabase** (Free PostgreSQL)
- **ElephantSQL** (Free tier)
- **Neon** (Free serverless Postgres)

## 🔧 Configuration

### Change AI Model

Edit `.env`:
```bash
OLLAMA_MODEL=llama3.1:8b  # or mistral, phi, etc.
```

### Adjust Voice Settings

Edit `frontend/src/services/speech.js` - modify rate, pitch, volume

### Add New Conversation Modes

1. Add mode to `backend/ai_service.py`
2. Add mode UI in `frontend/src/pages/Home.jsx`

## 📊 Database Schema

- **users** - User profiles and preferences
- **conversations** - Conversation sessions
- **messages** - All chat messages
- **message_feedback** - AI-generated feedback
- **user_progress** - Daily progress tracking

## 🐛 Troubleshooting

**Ollama not connecting:**
```bash
# Check if Ollama is running
ollama list

# If not, start it:
ollama serve
```

**Database connection failed:**
```bash
# Check PostgreSQL is running
psql -l

# Update DATABASE_URL in .env
```

**Speech recognition not working:**
- Use Chrome/Edge (best support)
- Allow microphone permissions
- Check HTTPS in production

## 🎯 Roadmap

- [ ] Group conversations (you + friend + AI)
- [ ] Voice analysis & scoring
- [ ] Conversation topics library
- [ ] Progress charts & statistics
- [ ] Export conversation transcripts
- [ ] Multiple languages support

## 📄 License

MIT License - Free to use and modify

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

**Built with ❤️ for English learners worldwide**
