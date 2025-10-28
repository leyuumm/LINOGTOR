# 🚀 Railway Deployment Guide - Earthquake Detector

## ✅ Prerequisites Completed
Your app is now ready for Railway deployment with:
- ✅ `Procfile` - Tells Railway how to run your app
- ✅ `requirements.txt` - Updated with gunicorn
- ✅ `runtime.txt` - Specifies Python 3.13
- ✅ `railway.json` - Railway configuration
- ✅ `.gitignore` - Prevents unnecessary files

---

## 📋 Step-by-Step Deployment (5 minutes)

### **Step 1: Push to GitHub** 🐙

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Earthquake Detector for Railway"
   ```

2. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Name: `earthquake-detector-bogo` (or your choice)
   - Make it **Public** or **Private**
   - Click "Create repository"

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/earthquake-detector-bogo.git
   git branch -M main
   git push -u origin main
   ```

---

### **Step 2: Deploy to Railway** 🚂

1. **Go to Railway**:
   - Visit: https://railway.app
   - Click **"Start a New Project"**
   - Sign up/Login with GitHub

2. **Connect Your Repo**:
   - Click **"Deploy from GitHub repo"**
   - Select your `earthquake-detector-bogo` repository
   - Click **"Deploy Now"**

3. **Wait for Build** (2-3 minutes):
   - Railway will automatically:
     - ✅ Detect Python
     - ✅ Install dependencies
     - ✅ Start your app with gunicorn
     - ✅ Give you a live URL!

4. **Get Your URL**:
   - Click on **"Settings"** tab
   - Scroll to **"Domains"**
   - Click **"Generate Domain"**
   - You'll get: `https://your-app.up.railway.app` 🎉

---

### **Step 3: Verify Deployment** ✅

1. **Check Logs**:
   - Click **"Deployments"** tab
   - View real-time logs
   - Should see: `"Serving Flask app 'app'"`

2. **Open Your App**:
   - Click your generated Railway URL
   - Your earthquake detector should load!
   - Test auto-refresh and alerts

3. **Monitor**:
   - Check **"Metrics"** for CPU/Memory usage
   - View **"Logs"** for PHIVOLCS data fetching

---

## 🎯 Important Railway Settings

### **Environment Variables** (if needed later):
- Go to **"Variables"** tab
- Add any API keys or secrets
- Example: `FLASK_ENV=production`

### **Custom Domain** (Optional):
- Go to **"Settings"** → **"Domains"**
- Click **"Custom Domain"**
- Add your own domain (if you have one)

---

## 💰 Railway Pricing

- **Free Tier**: $5 credit/month
- **Usage-based**: ~$0.000463/GB-hour
- **Your app**: Should stay well within free tier!

---

## 🔄 Auto-Deployment

Every time you push to GitHub:
```bash
git add .
git commit -m "Update earthquake detector"
git push
```

Railway will **automatically redeploy** your app! 🎉

---

## 🐛 Troubleshooting

### **Build Fails:**
- Check **"Deployments"** → **"View Logs"**
- Verify all files are pushed to GitHub
- Ensure `requirements.txt` is correct

### **App Won't Start:**
- Check `Procfile` syntax
- Verify gunicorn is in `requirements.txt`
- Check app logs for Python errors

### **502 Bad Gateway:**
- App might be starting (wait 30-60 seconds)
- Check if port binding is correct (Railway handles this automatically)

---

## 📞 Need Help?

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **GitHub Issues**: Create issue in your repo

---

## 🎉 Next Steps After Deployment

1. ✅ Test all features on live URL
2. ✅ Share URL with others
3. ✅ Monitor usage in Railway dashboard
4. ✅ Set up custom domain (optional)
5. ✅ Add more features and push updates!

---

**Ready to deploy?** Follow Step 1 above! 🚀

**Your live URL will be:**
`https://earthquake-detector-bogo.up.railway.app` (or similar)
