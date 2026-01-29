# Environment Configuration Guide

## Overview

This application automatically detects the environment and switches between AI providers:

- **Local Development**: Ollama + Local PostgreSQL
- **Production (Render)**: Groq + Render PostgreSQL

## Environment Detection

The app automatically detects production environment when:
- `ENVIRONMENT=production` is set
- `PORT` environment variable exists (Render sets this)
- Database URL contains "render.com", "railway", or "heroku"

## Setup Instructions

### Local Development

1. Make sure you have Ollama installed and running:
   ```bash
   # Install Ollama (if not already installed)
   curl https://ollama.ai/install.sh | sh
   
   # Pull the model
   ollama pull llama3.1:8b
   ```

2. Make sure PostgreSQL is running locally with database `englishbot`

3. Use the default `.env` file (already configured for local development)

### Production Deployment (Render)

1. Use the `.env.production` file as reference for environment variables
2. In Render dashboard, set these environment variables:
   - `ENVIRONMENT=production`
   - `DATABASE_URL=postgresql://english_bot_0jq7_user:zttnMss9GzxHeomhnlhecWHEcg7mUVAh@dpg-d5tkkd0gjchc73fcbis0-a.oregon-postgres.render.com/english_bot_0jq7`
   - `GROQ_API_KEY=your-groq-api-key-here`
   - `AI_PROVIDER=auto` (optional, defaults to auto)
   - Update `ALLOWED_ORIGINS` to include your production domain

## Provider Configuration

- **AI_PROVIDER=auto** (recommended): Automatically uses Ollama locally and Groq in production
- **AI_PROVIDER=groq**: Forces Groq usage (requires API key)
- **AI_PROVIDER=ollama**: Forces Ollama usage (requires local installation)

## Files Modified

- `backend/config.py`: Added environment detection and provider switching
- `backend/ai_service.py`: Updated to use effective provider
- `.env`: Local development configuration
- `.env.production`: Production configuration template

The application will now work seamlessly across both environments without manual configuration changes!