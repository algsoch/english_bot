# Render Deployment Guide

## Deployment Issues & Solutions

### Frontend (Static Site)
**Issue**: Render looking for `build` directory but Vite creates `dist`

**Solution**: Use these settings in Render dashboard:
- **Build Command**: `npm run build`
- **Publish Directory**: `dist`
- **Root Directory**: `frontend`

### Backend (Web Service)  
**Settings**:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run.py`
- **Environment**: `production`

### Environment Variables
Set these in Render dashboard:

**Frontend**:
- `VITE_API_URL`: `https://your-backend-service.onrender.com`
- `VITE_WS_URL`: `wss://your-backend-service.onrender.com`

**Backend**:
- `ENVIRONMENT`: `production`
- `AI_PROVIDER`: `auto`
- `GROQ_API_KEY`: `your-actual-groq-key`
- `DATABASE_URL`: `your-postgres-connection-string`
- `ALLOWED_ORIGINS`: `https://your-frontend-service.onrender.com`

### Deployment Steps

1. **Create Backend Service First**:
   - Type: Web Service
   - Repository: `https://github.com/algsoch/english_bot`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run.py`
   - Add environment variables above

2. **Create Frontend Service**:
   - Type: Static Site  
   - Repository: `https://github.com/algsoch/english_bot`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Publish Directory: `dist`
   - Add frontend environment variables with backend URL

3. **Update CORS**: Add frontend URL to backend `ALLOWED_ORIGINS`