# 🤖 English Bot - AI-Powered Conversation Practice

An intelligent English conversation practice application that helps users improve their speaking skills through AI-powered interactions.

## 🎬 Demo Video
📹 **[Watch Demo on YouTube](https://www.youtube.com/watch?v=tN8zLuT8uJ8)**

## ✨ Features

### 🎯 Core Functionality
- 🎤 **Speech Recognition** - Real-time voice input with Web Speech API
- 🔊 **Text-to-Speech** - Natural AI voice responses  
- 💬 **Multiple Conversation Modes**:
  - Free Talk - Natural conversations
  - Grammar Focus - Grammar correction and practice
  - Vocabulary Building - Learn new words
  - Pronunciation Practice - Improve accent
  - Business English - Professional communication
  - Travel English - Practical travel phrases
- 🎭 **AI Personalities**: Choose between Teacher, Girlfriend, or Friend modes
- 📊 **Progress Tracking** - Monitor your learning journey with detailed analytics
- 📱 **Mobile Optimized** - PWA support for mobile devices

### 🧠 AI Technology
- **Environment Auto-Detection**: Automatically switches between:
  - **Local Development**: Ollama (100% free, runs offline)
  - **Production**: Groq API (fast cloud inference)
- **Smart Responses**: Context-aware conversations with personality matching
- **Learning Analytics**: Track improvement over time with detailed metrics

## 🛠️ Tech Stack

**Backend:**
- FastAPI (async Python web framework)
- PostgreSQL (database with conversation history)
- WebSocket (real-time communication)
- AI Providers:
  - Ollama (local AI - llama3.1:8b)
  - Groq API (production - llama-3.3-70b-versatile)

**Frontend:**
- React 18 + Vite (modern frontend)
- TailwindCSS (responsive styling) 
- Framer Motion (smooth animations)
- Web Speech API (voice recognition)
- Zustand (state management)
- Recharts (progress visualization)

**Database Schema:**
- Users & Profiles
- Conversation Sessions
- Message History
- Learning Progress Analytics
- Feedback System

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 18+
- PostgreSQL
- Ollama (for local) OR Groq API key (for cloud)

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/algsoch/english_bot.git
cd english_bot
```

2. **Backend Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment setup
cp .env.template .env
# Edit .env with your settings
```

3. **Frontend Setup**  
```bash
cd frontend
npm install
cp .env.example .env
# Configure frontend environment
```

4. **Database Setup**
```bash
# Create database
createdb englishbot

# Run schema
psql -d englishbot -f database/schema.sql
```

5. **AI Provider Setup**

**Option A - Local (Free):**
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3.1:8b
```

**Option B - Cloud (Groq):**
- Get API key from [Groq Console](https://console.groq.com/keys)
- Add to `.env`: `GROQ_API_KEY=your-key-here`

### Running the App

**Start Backend:**
```bash
python run.py
# OR: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

Visit: `http://localhost:5173`

## 📁 Project Structure

```
english_bot/
├── backend/                 # FastAPI Backend
│   ├── ai_service.py       # AI provider management
│   ├── config.py           # Environment configuration  
│   ├── database.py         # Database connection
│   ├── main.py             # FastAPI application
│   ├── models.py           # SQLAlchemy models
│   └── schemas.py          # Pydantic schemas
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API & WebSocket
│   │   └── store/          # State management
│   └── public/             # Static assets
├── database/
│   └── schema.sql          # PostgreSQL schema
├── .env.template           # Environment template
├── requirements.txt        # Python dependencies
└── README.md
```

## ⚙️ Configuration

The app automatically detects environment and configures AI providers:

### Local Development (Automatic)
- Uses **Ollama** locally (free, private)
- Local PostgreSQL database
- Perfect for development and privacy

### Production/Cloud (Automatic)  
- Uses **Groq API** (fast, cloud-based)
- Production PostgreSQL (Render/Railway)
- Optimized for deployment

### Environment Variables
```env
# Auto-detection
ENVIRONMENT=development
AI_PROVIDER=auto

# Groq (Production)
GROQ_API_KEY=your-api-key
GROQ_MODEL=llama-3.3-70b-versatile

# Ollama (Local)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/englishbot
```

## 🌍 Deployment

### Render (Recommended)
1. Fork this repository
2. Create Web Service on Render
3. Set environment variables:
   - `ENVIRONMENT=production`
   - `DATABASE_URL=your-postgres-url`
   - `GROQ_API_KEY=your-api-key`
4. Deploy automatically!

### Local Docker
```bash
docker-compose up --build
```

## 🎮 How to Use

### 1. Choose AI Personality
- 👨‍🏫 **Teacher**: Professional, educational feedback
- 💕 **Girlfriend**: Casual, friendly conversations
- 👫 **Friend**: Relaxed, buddy-like chat

### 2. Select Learning Mode
- **Free Talk**: Natural conversation practice
- **Grammar Focus**: Corrections and explanations
- **Vocabulary**: Learn new words in context
- **Pronunciation**: Accent and clarity improvement
- **Business**: Professional communication
- **Travel**: Practical phrases and situations

### 3. Start Practicing
- Click microphone for voice input
- Type messages for text chat
- Get real-time AI feedback
- Track your progress over time

## 📊 Features in Detail

### Voice Recognition
- Real-time speech-to-text
- Multiple language support
- Noise filtering and echo prevention
- Mobile device compatibility

### AI Responses  
- Context-aware conversations
- Personality-matched responses
- Grammar corrections with explanations
- Vocabulary suggestions and definitions

### Progress Analytics
- Conversation history tracking
- Speaking time and accuracy metrics
- Grammar improvement over time
- Vocabulary growth measurement

### Learning Modes
- **Free Talk**: Natural conversation flow
- **Grammar Focus**: Detailed corrections
- **Vocabulary**: Word learning in context
- **Pronunciation**: Accent improvement
- **Business**: Professional scenarios
- **Travel**: Practical situations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📝 License

MIT License - feel free to use this project for learning and development.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - Frontend library
- [Ollama](https://ollama.ai/) - Local AI models
- [Groq](https://groq.com/) - Fast AI inference
- [PostgreSQL](https://www.postgresql.org/) - Reliable database

---

**🎯 Perfect for English learners who want to practice speaking with AI assistance!**

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
