# 🚀 AI News Website Deployment Guide

This guide will help you deploy your AI News website with a React frontend and Python Flask backend.

## 📋 Prerequisites

1. **Gemini API Key**: Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **GitHub Account**: For code hosting
3. **Vercel Account**: For frontend deployment
4. **Railway Account**: For backend deployment

## 🔧 Step 1: Prepare Your Code

### Push to GitHub
```bash
# Initialize git if not done already
git init
git add .
git commit -m "Initial commit - AI News Platform"

# Create a new repository on GitHub and push
git remote add origin https://github.com/yourusername/ai-news.git
git branch -M main
git push -u origin main
```

## 🌐 Step 2: Deploy Backend (Railway)

### 2.1 Create Railway Account
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub

### 2.2 Deploy Backend
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your `ai-news` repository
4. Railway will auto-detect Python and deploy

### 2.3 Set Environment Variables
In Railway dashboard:
1. Go to your project
2. Click **"Variables"** tab
3. Add these environment variables:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   RAILWAY_ENVIRONMENT=production
   ```

### 2.4 Get Backend URL
1. In Railway dashboard, go to **"Settings"** tab
2. Copy the **"Public Domain"** URL (e.g., `https://your-app.railway.app`)
3. **Save this URL** - you'll need it for frontend deployment

## 💻 Step 3: Deploy Frontend (Vercel)

### 3.1 Create Vercel Account
1. Go to [Vercel.com](https://vercel.com)
2. Sign up with GitHub

### 3.2 Deploy Frontend
1. Click **"New Project"**
2. Import your GitHub repository
3. Vercel will auto-detect Vite

### 3.3 Set Environment Variables
In Vercel dashboard:
1. Go to **"Settings"** → **"Environment Variables"**
2. Add:
   ```
   VITE_API_URL=https://your-railway-backend-url.railway.app
   ```
   (Replace with your actual Railway backend URL from Step 2.4)

### 3.4 Deploy
1. Click **"Deploy"**
2. Vercel will build and deploy your frontend
3. You'll get a URL like `https://your-app.vercel.app`

## ✅ Step 4: Test Your Deployment

1. **Visit your Vercel URL**
2. **Test the refresh functionality**:
   - Click the refresh button
   - Try the dropdown menu options
   - Verify articles are loading

## 🔧 Step 5: Custom Domain (Optional)

### For Frontend (Vercel):
1. Go to Vercel dashboard → **"Domains"**
2. Add your custom domain
3. Follow DNS setup instructions

### For Backend (Railway):
1. Go to Railway dashboard → **"Settings"**
2. Add custom domain in **"Domains"** section

## 🛠️ Troubleshooting

### Backend Issues:
- Check Railway logs in dashboard
- Verify `GEMINI_API_KEY` is set correctly
- Ensure all dependencies are in `requirements.txt`

### Frontend Issues:
- Check Vercel build logs
- Verify `VITE_API_URL` points to correct Railway URL
- Test API connectivity from browser dev tools

### CORS Issues:
- Backend already has CORS enabled
- If issues persist, check Railway logs

## 📊 Monitoring

### Railway (Backend):
- View logs in real-time
- Monitor resource usage
- Set up alerts

### Vercel (Frontend):
- Analytics dashboard
- Performance monitoring
- Build status

## 🔄 Updates

### Backend Updates:
1. Push changes to GitHub
2. Railway auto-deploys from main branch

### Frontend Updates:
1. Push changes to GitHub  
2. Vercel auto-deploys from main branch

## 💡 Tips

1. **Environment Variables**: Never commit API keys to git
2. **Monitoring**: Set up alerts for both services
3. **Backup**: Keep your Gemini API key secure
4. **Testing**: Test in production environment before announcing
5. **Performance**: Monitor scraper performance and adjust if needed

## 🚀 Going Live Checklist

- [ ] Backend deployed on Railway
- [ ] Environment variables set correctly
- [ ] Frontend deployed on Vercel
- [ ] API URL configured properly
- [ ] Refresh functionality working
- [ ] Topics generation working
- [ ] Mobile responsive design verified
- [ ] Custom domain configured (optional)
- [ ] Analytics set up (optional)

## 📞 Support

If you encounter issues:
1. Check service status pages
2. Review logs in dashboards
3. Test API endpoints directly
4. Verify environment variables

Your AI News platform is now live! 🎉 