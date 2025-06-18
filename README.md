# 🤖 Russian Telegram Sentiment Analysis Bot

An advanced Telegram bot that performs real-time sentiment analysis on Russian chat messages using state-of-the-art multilingual AI models.

## ✨ Features

- 🎯 **Advanced Sentiment Analysis**: Uses `cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual` - one of the best multilingual sentiment models
- 🇷🇺 **Russian Language Optimized**: Excellent performance on Russian text, slang, and informal language
- 📊 **Granular 1-10 Scoring**: Provides nuanced sentiment scores from 1 (very negative) to 10 (very positive)
- 🚨 **Outlier Detection**: Automatically flags extremely positive/negative messages
- 📈 **Daily Reports**: Generates comprehensive sentiment analytics
- 🔇 **Silent Operation**: Monitors without responding to messages
- 💾 **Data Logging**: Saves all sentiment data in JSON format
- 🌐 **24/7 Cloud Hosting**: Ready for deployment on free cloud platforms

## 🚀 Quick Start

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd telegram-sentiment-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**:
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env file with your credentials
   nano .env  # or use any text editor
   ```
   
   **Required values to set in `.env`**:
   - `BOT_TOKEN`: Your bot token from @BotFather
   - `MONITOR_CHAT_ID`: The chat ID to monitor (use `python get_chat_id.py` to find it)

4. **Run the bot**:
   ```bash
   python bot.py
   ```

### 🌐 Deploy to Cloud (24/7 Hosting)

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed instructions on deploying to:
- **Railway** (Recommended - $5/month free credit)
- **Render** (750 hours/month free)
- **Heroku** (Free tier available)

## 📊 Model Performance

The bot now uses **XLM-RoBERTa multilingual model** which provides:

| Text Example | Score | Analysis |
|--------------|--------|----------|
| "Пиздец" | 1.1/10 | Correctly identifies strong profanity as very negative |
| "супер, спасибо" | 9.9/10 | Perfect detection of positive gratitude |
| "Вот это да!" | 9.9/10 | Excellent handling of Russian exclamations |
| "заебали" | 1.2/10 | Properly detects vulgar negative sentiment |

### 🎯 Key Improvements Over Previous Model:
- ✅ **Better context understanding** for mixed sentiment
- ✅ **Improved granularity** (1.1, 1.8, 9.9 vs rigid 1.0, 3.0, 10.0)
- ✅ **Superior handling** of Russian slang and profanity
- ✅ **Twitter-optimized** for social media content
- ✅ **Multilingual support** for mixed-language chats

## 🔧 Configuration

### Environment Variables

```bash
BOT_TOKEN=your_telegram_bot_token
MONITOR_CHAT_ID=your_chat_id_to_monitor
MODEL_NAME=cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual
SENTIMENT_THRESHOLD_LOW=3.0    # Below this = negative outlier
SENTIMENT_THRESHOLD_HIGH=7.5   # Above this = positive outlier
```

### Thresholds

- **Negative Outlier**: ≤ 3.0/10
- **Neutral Range**: 3.1-7.4/10  
- **Positive Outlier**: ≥ 7.5/10

## 📁 Project Structure

```
├── bot.py                 # Main entry point
├── telegram_bot.py        # Bot logic and message handling
├── sentiment_analyzer.py  # ML sentiment analysis engine
├── config.py             # Configuration and environment variables
├── requirements.txt      # Python dependencies
├── Procfile             # Heroku deployment
├── runtime.txt          # Python version specification
├── railway.toml         # Railway deployment config
├── render.yaml          # Render deployment config
├── DEPLOYMENT.md        # Detailed deployment guide
└── logs/                # Sentiment data and reports
    ├── sentiment_log_YYYY-MM-DD.json
    ├── outliers_YYYY-MM.json
    └── daily_report_YYYY-MM-DD.json
```

## 📊 Data Output

### Sentiment Log Entry
```json
{
  "timestamp": "2025-01-18T15:30:45",
  "chat_id": -673515655,
  "user_id": 123456789,
  "username": "user123",
  "message": "Отличная работа!",
  "sentiment_score": 8.7,
  "sentiment_label": "POSITIVE",
  "is_outlier": true
}
```

### Daily Report
```json
{
  "date": "2025-01-18",
  "total_messages": 156,
  "average_sentiment": 5.8,
  "outliers_count": 12,
  "sentiment_distribution": {
    "positive": 67,
    "neutral": 78,
    "negative": 11
  },
  "top_positive": 9.9,
  "top_negative": 1.1
}
```

## 🎯 Use Cases

- **Community Management**: Monitor chat sentiment trends
- **Customer Support**: Track satisfaction levels
- **Social Research**: Analyze group communication patterns
- **Content Moderation**: Identify extremely negative interactions
- **Business Analytics**: Understand audience reactions

## 🔐 Security & Privacy

- ✅ Bot operates in **silent mode** (no message replies)
- ✅ Sensitive tokens stored as **environment variables**
- ✅ No personal data beyond usernames stored
- ✅ All data kept locally in JSON logs
- ✅ GDPR-friendly logging practices

## 🛠️ Technical Details

- **AI Model**: XLM-RoBERTa multilingual (1.1GB)
- **Memory Usage**: 1-2GB RAM
- **Languages**: Optimized for Russian, supports 30+ languages
- **Response Time**: <1 second per message
- **Throughput**: 1000+ messages/day on free tier

## 📈 Performance Monitoring

The bot provides comprehensive logging:
- Real-time sentiment analysis
- Outlier detection and alerts
- Daily sentiment summaries
- Session statistics
- Error tracking and recovery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the [DEPLOYMENT.md](DEPLOYMENT.md) guide
2. Review the configuration in `config.py`
3. Check bot logs for error messages
4. Verify environment variables are set correctly

---

**Ready to deploy?** Check out **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step cloud hosting instructions! 🚀 