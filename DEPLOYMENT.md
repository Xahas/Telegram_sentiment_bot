# 🚀 Telegram Sentiment Bot - Deployment Guide

This guide will help you deploy your Telegram sentiment analysis bot on various free hosting platforms for 24/7 operation.

## 📋 Prerequisites

1. Your bot files (already prepared ✅)
2. A GitHub account
3. Your Telegram bot token: `8028342158:AAHqYTygCaSFuFQrBL6Jl3qMY1pADZQ7tSo`
4. Your chat ID: `-673515655`

## 🏗️ Deployment Options

### 🥇 Option 1: Railway (Recommended)

**Pros:** $5 free credit monthly, excellent for small bots, great performance
**Steps:**

1. Create a [Railway account](https://railway.app)
2. Push your code to GitHub (see GitHub setup below)
3. In Railway dashboard, click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables:
   - `BOT_TOKEN`: `8028342158:AAHqYTygCaSFuFQrBL6Jl3qMY1pADZQ7tSo`
   - `MONITOR_CHAT_ID`: `-673515655`
6. Deploy! 🚀

### 🥈 Option 2: Render

**Pros:** 750 hours/month free (24/7 coverage), automatic scaling
**Steps:**

1. Create a [Render account](https://render.com)
2. Push code to GitHub
3. In Render dashboard, click "New" → "Background Worker"
4. Connect your GitHub repository
5. Use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
6. Add environment variables (same as Railway)
7. Deploy! 🚀

### 🥉 Option 3: Heroku

**Pros:** Easy deployment, well-documented
**Cons:** May sleep after 30 minutes of inactivity
**Steps:**

1. Create a [Heroku account](https://heroku.com)
2. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Push code to GitHub
4. In Heroku dashboard, create new app
5. Connect to GitHub repository
6. Set Config Vars (environment variables)
7. Deploy from GitHub branch

## 📁 GitHub Setup

1. Create a new repository on GitHub
2. Upload these files:
   ```
   ├── bot.py
   ├── telegram_bot.py
   ├── sentiment_analyzer.py
   ├── config.py
   ├── requirements.txt
   ├── Procfile
   ├── runtime.txt
   ├── railway.toml
   ├── render.yaml
   └── README.md
   ```

3. **Important:** Create a `.env` file locally but DON'T upload it to GitHub
4. Instead, use the platform's environment variable settings

## 🔐 Environment Variables Setup

For any platform, set these environment variables:

```
BOT_TOKEN=8028342158:AAHqYTygCaSFuFQrBL6Jl3qMY1pADZQ7tSo
MONITOR_CHAT_ID=-673515655
MODEL_NAME=cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual
SENTIMENT_THRESHOLD_LOW=3.0
SENTIMENT_THRESHOLD_HIGH=7.5
LOG_DIRECTORY=logs
DAILY_REPORT_TIME=23:59
```

## 📊 Resource Requirements

- **RAM:** 1-2GB (for the ML model)
- **CPU:** 1 core sufficient
- **Storage:** 1GB for logs and model cache
- **Network:** Minimal (only Telegram API calls)

## 🔍 Monitoring Your Bot

After deployment, check:

1. **Logs:** Watch for startup messages and sentiment analysis
2. **Memory usage:** ML model uses ~800MB-1.2GB RAM
3. **Response time:** Should be immediate for sentiment analysis
4. **Log files:** Check if sentiment data is being saved

## 🐛 Troubleshooting

**Bot not responding:**
- Check environment variables are set correctly
- Verify bot token is valid
- Check logs for startup errors

**High memory usage:**
- Normal for ML models (1-2GB)
- Consider using a smaller model if needed

**Model loading fails:**
- Check internet connection during startup
- Verify HuggingFace access
- May take 30-60 seconds on first run

## 🎯 Quick Start (Railway - Fastest)

1. Fork this repository on GitHub
2. Go to [railway.app](https://railway.app)
3. Sign up with GitHub
4. Click "Deploy from GitHub"
5. Select your forked repository
6. Add the environment variables above
7. Click Deploy
8. Your bot will be live in 2-3 minutes! 🎉

## 📈 Scaling & Monitoring

- **Free tiers** handle 1000+ messages/day easily
- **Paid upgrades** available if you need more resources
- **Monitoring:** All platforms provide logs and usage metrics
- **Backups:** Sentiment data saved in JSON files

## 🔒 Security Notes

- ✅ Bot token stored as environment variable
- ✅ No sensitive data in code repository
- ✅ Logs contain sentiment data but no private info
- ✅ Bot operates in silent mode (no replies)

Your bot is now ready for 24/7 deployment! 🤖🚀 