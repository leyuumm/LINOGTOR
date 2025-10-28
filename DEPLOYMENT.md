# Deploying Real-Time Earthquake Detector to Vercel

## Prerequisites
1. Install Vercel CLI: `npm install -g vercel`
2. Create a Vercel account at https://vercel.com

## Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Open terminal in project directory**
   ```powershell
   cd "C:\Users\Lliam Khenzo Monleon\OneDrive - MSFT\Wired in\Earthquake Detector Realtime"
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy to Vercel**
   ```bash
   vercel
   ```
   - Follow the prompts
   - Select your account
   - Link to existing project or create new one
   - Accept default settings

4. **Deploy to Production**
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via GitHub

1. **Push code to GitHub repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Earthquake Detector"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Connect to Vercel**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Vercel will auto-detect Flask and deploy

## Important Notes

### ⚠️ Limitations on Vercel:
1. **Serverless Functions** - Each API call runs independently (no persistent connections)
2. **10 Second Timeout** - Functions timeout after 10 seconds (may affect PHIVOLCS scraping)
3. **Cold Starts** - First request may be slower
4. **No WebSockets** - Auto-refresh works, but purely client-side polling

### ✅ What Works on Vercel:
- ✅ All API endpoints (`/api/earthquakes`, `/api/stats`, `/api/phivolcs-news`, `/api/hazard-hunter`)
- ✅ Frontend interface with auto-refresh
- ✅ Alert notifications and sounds
- ✅ Map visualization
- ✅ USGS and PHIVOLCS data fetching

### 🔄 Alternative: Deploy to Railway/Render (Better for Flask)

If you experience issues with Vercel, consider these alternatives that support persistent Flask servers:

**Railway.app:**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

**Render.com:**
- Create account at https://render.com
- Connect GitHub repo
- Select "Web Service"
- Set build command: `pip install -r requirements.txt`
- Set start command: `gunicorn app:app`

## After Deployment

Your app will be available at:
- Vercel: `https://your-project-name.vercel.app`
- Railway: `https://your-project-name.up.railway.app`
- Render: `https://your-project-name.onrender.com`

## Need Help?
- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs

---
**Copyright © 2025 Lliam Khenzo P. Monleon. All Rights Reserved.**
