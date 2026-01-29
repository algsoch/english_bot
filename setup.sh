#!/bin/bash

# AI Speaking Partner - Setup Script

echo "🚀 Setting up AI Speaking Partner..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check PostgreSQL
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL found${NC}"
else
    echo -e "${RED}✗ PostgreSQL not found. Please install PostgreSQL first.${NC}"
    exit 1
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama found${NC}"
    
    # Check if llama3.1:8b is installed
    if ollama list | grep -q "llama3.1:8b"; then
        echo -e "${GREEN}✓ llama3.1:8b model found${NC}"
    else
        echo -e "${YELLOW}! llama3.1:8b not found. Pulling model...${NC}"
        ollama pull llama3.1:8b
    fi
else
    echo -e "${RED}✗ Ollama not found. Please install Ollama first.${NC}"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python found${NC}"
else
    echo -e "${RED}✗ Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js found${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

# Setup database
echo ""
echo "🗄️  Setting up database..."
createdb englishbot 2>/dev/null || echo -e "${YELLOW}Database already exists${NC}"

if [ -f "database/schema.sql" ]; then
    psql -d englishbot -f database/schema.sql
    echo -e "${GREEN}✓ Database schema created${NC}"
else
    echo -e "${RED}✗ Schema file not found${NC}"
    exit 1
fi

# Setup environment
echo ""
echo "⚙️  Configuring environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Environment file created${NC}"
    echo -e "${YELLOW}! Please edit .env if needed${NC}"
else
    echo -e "${YELLOW}! .env already exists${NC}"
fi

# Create virtual environment
echo ""
echo "🐍 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}! Virtual environment already exists${NC}"
fi

# Activate and install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Install Node dependencies
echo ""
echo "📦 Installing Node dependencies..."
cd frontend
npm install
cd ..
echo -e "${GREEN}✓ Node dependencies installed${NC}"

# Done
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "🎯 To start the application:"
echo ""
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Start backend:"
echo "     python -m backend.main"
echo ""
echo "  3. Start frontend in new terminal:"
echo "     cd frontend && npm run dev"
echo ""
echo "  4. Open http://localhost:5173"
echo ""
echo "💡 Tip: Keep venv activated while running the backend"
echo ""
echo "Happy learning! 🎓"
