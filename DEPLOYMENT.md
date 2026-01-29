# Deployment Configuration Guide

## Environment Variables Setup

### Frontend (.env in frontend/)
```bash
# For local development
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# For production deployment (Render, Vercel, etc.)
VITE_API_URL=https://your-backend-domain.com
VITE_WS_URL=wss://your-backend-domain.com
```

### Backend (.env in root/)
```bash
# For production deployment
DATABASE_URL=postgresql://username:password@host:port/database
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
APP_HOST=0.0.0.0
APP_PORT=8000
```

## Render Deployment

### Backend (API Service)
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python -m backend.main`
4. Add environment variables:
   - `DATABASE_URL`: Your Render PostgreSQL connection string
   - `GROQ_API_KEY`: Your Groq API key
   - `ALLOWED_ORIGINS`: Your frontend URLs
   - `APP_HOST=0.0.0.0`
   - `APP_PORT=8000`

### Frontend (Static Site)
1. Connect your GitHub repository
2. Set build directory: `frontend`
3. Set build command: `npm install && npm run build`
4. Set publish directory: `dist`
5. Add environment variable:
   - `VITE_API_URL`: Your backend service URL (https://your-backend.onrender.com)
   - `VITE_WS_URL`: Your backend WebSocket URL (wss://your-backend.onrender.com)

## Vercel Deployment

### Frontend
1. Import project from GitHub
2. Set framework preset to Vite
3. Set root directory to `frontend`
4. Add environment variables:
   - `VITE_API_URL`: Your backend URL
   - `VITE_WS_URL`: Your backend WebSocket URL

## Railway/Heroku Deployment

Similar process with platform-specific configuration files.

## Important Notes

- Always use environment variables, never hardcode URLs
- Use relative paths (`/api/...`) when possible
- WebSocket URLs should use `wss://` in production
- API URLs should use `https://` in production
- Ensure CORS is configured properly in backend