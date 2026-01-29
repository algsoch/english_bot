# 🚨 RENDER DASHBOARD SETTINGS - MUST UPDATE THESE

## ⚠️ Current Problem
Render is still using old settings:
- ❌ Build Command: `npm install` (wrong)
- ❌ Publish Directory: `build` (wrong)

## ✅ Required Changes in Render Dashboard

### Step 1: Go to Your Render Service Settings
1. Go to https://dashboard.render.com
2. Click on your `english_bot` service
3. Go to **Settings** tab

### Step 2: Update These Exact Settings

**Build & Deploy**:
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Publish Directory**: `dist`

### Step 3: Environment Variables (if not set)
Add these in **Environment** tab:
```
VITE_API_URL=https://your-backend-service.onrender.com
VITE_WS_URL=wss://your-backend-service.onrender.com
```

### Step 4: Save & Redeploy
1. Click **Save Changes**
2. Render will automatically redeploy with correct settings

## 🎯 Expected Result
After updating settings, the build should:
1. Run `npm run build` ✅
2. Create `dist` directory ✅  
3. Deploy successfully ✅

## 📋 Double-Check List
- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm run build`
- [ ] Publish Directory: `dist`
- [ ] Environment variables set
- [ ] Saved and redeployed