import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

def get_required_env(var_name: str) -> str:
    """Get required environment variable or exit with error."""
    value = os.getenv(var_name)
    if not value:
        print(f"ERROR: Required environment variable {var_name} is not set!")
        print(f"Please set {var_name} in your environment or .env file")
        sys.exit(1)
    return value

# Bot configuration - REQUIRED
BOT_TOKEN = get_required_env("BOT_TOKEN")

# Chat monitoring - REQUIRED (set to specific chat ID)
MONITOR_CHAT_ID = int(get_required_env("MONITOR_CHAT_ID"))

# Sentiment analysis model
# Updated to use state-of-the-art multilingual model that excels at Russian sentiment
MODEL_NAME = os.getenv("MODEL_NAME", "cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual")

# Sentiment outlier thresholds (1-10 scale)
SENTIMENT_THRESHOLD_LOW = float(os.getenv("SENTIMENT_THRESHOLD_LOW", "3.0"))   # Below this = negative outlier
SENTIMENT_THRESHOLD_HIGH = float(os.getenv("SENTIMENT_THRESHOLD_HIGH", "7.5"))  # Above this = positive outlier

# Logging
LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "logs")
DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "23:59")  # Time for daily reports (HH:MM format)

# Sentiment scale mapping (1-10)
SENTIMENT_SCALE_MIN = 1
SENTIMENT_SCALE_MAX = 10 