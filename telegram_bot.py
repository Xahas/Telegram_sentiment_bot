#!/usr/bin/env python3
"""
Telegram Sentiment Analysis Bot
Silently monitors Russian chat messages and logs sentiment analysis results.
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import schedule
import time
from threading import Thread

from telegram import Update, Message
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import aiofiles

from config import (
    BOT_TOKEN, 
    MONITOR_CHAT_ID, 
    LOG_DIRECTORY,
    SENTIMENT_THRESHOLD_LOW,
    SENTIMENT_THRESHOLD_HIGH,
    DAILY_REPORT_TIME,
    MODEL_NAME
)
from sentiment_analyzer import RussianSentimentAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIRECTORY}/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SentimentBot:
    """
    Silent Telegram bot for sentiment analysis monitoring.
    """
    
    def __init__(self):
        """Initialize the sentiment bot."""
        self.application = None
        self.analyzer = None
        self.session_messages = []
        self.session_outliers = 0
        self.is_running = False
        self.target_chat_id = MONITOR_CHAT_ID
        
        # Ensure logs directory exists
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
        
        logger.info("Sentiment Bot initialized")
    
    async def initialize(self) -> bool:
        """
        Setup the bot and sentiment analyzer.
        
        Returns:
            bool: True if setup successful
        """
        try:
            # Initialize sentiment analyzer
            logger.info("Initializing sentiment analyzer...")
            self.analyzer = RussianSentimentAnalyzer(MODEL_NAME)
            self.analyzer.load_model()
            
            # Create application
            self.application = Application.builder().token(BOT_TOKEN).build()
            
            # Add message handler for all text messages
            message_handler = MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.handle_message
            )
            self.application.add_handler(message_handler)
            
            # Add error handler
            self.application.add_error_handler(self.error_handler)
            
            logger.info("✅ Bot setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup bot: {e}")
            return False
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle incoming messages - analyze sentiment silently.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        try:
            message = update.message
            if not message or not message.text:
                return
            
            # Check if this is the monitored chat (if specified)
            if self.target_chat_id and message.chat_id != self.target_chat_id:
                return
            
            # Log chat ID for setup purposes
            if not self.target_chat_id:
                logger.info(f"💡 Message from chat ID: {message.chat_id}")
                logger.info("💡 Update your config.py with this chat ID to monitor this chat")
            
            # Analyze sentiment
            sentiment_score, sentiment_label = self.analyzer.analyze_sentiment(message.text)
            
            # Create message data
            message_data = {
                "message_id": message.message_id,
                "chat_id": message.chat_id,
                "user_id": message.from_user.id if message.from_user else None,
                "username": message.from_user.username if message.from_user else None,
                "text": message.text,
                "timestamp": message.date.isoformat(),
                "sentiment_score": sentiment_score,
                "sentiment_label": sentiment_label
            }
            
            # Store sentiment data
            self.session_messages.append(message_data)
            
            # Check for outliers
            is_outlier = self.analyzer.is_outlier(
                sentiment_score, 
                SENTIMENT_THRESHOLD_LOW, 
                SENTIMENT_THRESHOLD_HIGH
            )
            
            if is_outlier:
                self.session_outliers += 1
                outlier_type = "negative" if sentiment_score <= SENTIMENT_THRESHOLD_LOW else "positive"
                
                logger.info(f"🚨 Outlier detected: {outlier_type} sentiment {sentiment_score}/10")
                logger.info(f"📝 Message: {message.text[:50]}...")
                
                # Save outlier to special log
                outlier_filename = f"outliers_{datetime.now().strftime('%Y-%m')}.json"
                self._save_to_json(message_data, outlier_filename)
            
            # Log sentiment analysis
            logger.info(f"📊 Sentiment: {sentiment_score}/10 ({sentiment_label})")
            
            # Save data periodically (every 10 messages)
            if len(self.session_messages) % 10 == 0:
                await self.save_current_data()
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors in bot operation."""
        logger.error(f"Update {update} caused error {context.error}")
    
    async def save_current_data(self) -> None:
        """Save current sentiment data to file."""
        try:
            if not self.session_messages:
                return
            
            today = datetime.now().strftime("%Y-%m-%d")
            data_file = f"{LOG_DIRECTORY}/sentiment_data_{today}.json"
            
            # Append to existing data or create new file
            existing_data = []
            if os.path.exists(data_file):
                async with aiofiles.open(data_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if content.strip():
                        existing_data = json.loads(content)
            
            # Combine data
            all_data = existing_data + self.session_messages
            
            # Save updated data
            async with aiofiles.open(data_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(all_data, ensure_ascii=False, indent=2))
            
            logger.info(f"💾 Saved {len(self.session_messages)} sentiment records")
            self.session_messages.clear()  # Clear memory after saving
            
        except Exception as e:
            logger.error(f"Error saving sentiment data: {e}")
    
    async def generate_daily_report(self) -> None:
        """Generate daily sentiment report."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            report_filename = f"daily_report_{today}.json"
            
            # Calculate statistics from today's messages
            today_messages = [
                msg for msg in self.session_messages 
                if msg["timestamp"].startswith(today)
            ]
            
            if not today_messages:
                logger.info("📊 No messages today for daily report")
                return
            
            # Calculate statistics
            scores = [msg["sentiment_score"] for msg in today_messages]
            avg_sentiment = sum(scores) / len(scores)
            
            outliers = [msg for msg in today_messages if msg["is_outlier"]]
            
            report = {
                "date": today,
                "total_messages": len(today_messages),
                "average_sentiment": round(avg_sentiment, 2),
                "outliers_count": len(outliers),
                "sentiment_distribution": {
                    "positive": len([s for s in scores if s >= 6.5]),
                    "neutral": len([s for s in scores if 3.5 < s < 6.5]),
                    "negative": len([s for s in scores if s <= 3.5])
                },
                "top_positive": max(scores) if scores else 0,
                "top_negative": min(scores) if scores else 0,
                "generated_at": datetime.now().isoformat()
            }
            
            # Save report
            self._save_to_json(report, report_filename)
            logger.info(f"📈 Daily report generated: {report_filename}")
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
    
    def schedule_daily_reports(self) -> None:
        """Schedule daily report generation."""
        def run_report():
            asyncio.run(self.generate_daily_report())
        
        schedule.every().day.at(DAILY_REPORT_TIME).do(run_report)
        logger.info(f"📅 Daily reports scheduled for {DAILY_REPORT_TIME}")
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Run scheduler in background thread
        scheduler_thread = Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def run(self) -> None:
        """Run the bot."""
        try:
            # Setup
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            setup_success = loop.run_until_complete(self.initialize())
            if not setup_success:
                logger.error("Failed to setup bot")
                return
            
            # Start scheduler
            self.is_running = True
            self.schedule_daily_reports()
            
            # Display startup info
            print("\n" + "="*60)
            print("🤖 TELEGRAM SENTIMENT ANALYSIS BOT STARTED")
            print("="*60)
            print(f"📊 Model: {MODEL_NAME}")
            print(f"🎯 Monitoring: {'All chats' if not self.target_chat_id else f'Chat ID {self.target_chat_id}'}")
            print(f"📝 Logs: {LOG_DIRECTORY}/")
            print(f"📅 Daily reports: {DAILY_REPORT_TIME}")
            print(f"⚠️  Outlier thresholds: ≤{SENTIMENT_THRESHOLD_LOW} (negative), ≥{SENTIMENT_THRESHOLD_HIGH} (positive)")
            print("🔇 Silent mode: Bot will NOT respond to messages")
            print("="*60)
            
            if not self.target_chat_id:
                print("💡 SETUP TIP: Send a message in your target chat to see the Chat ID,")
                print("   then update MONITOR_CHAT_ID in config.py")
                print("="*60)
            
            # Start bot
            self.application.run_polling(
                poll_interval=1.0,
                drop_pending_updates=True
            )
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error running bot: {e}")
        finally:
            self.is_running = False
            # Save any remaining data
            if hasattr(self, 'session_messages') and self.session_messages:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.save_current_data())
                loop.close()
            if self.session_outliers:
                logger.info(f"💾 Session outliers: {self.session_outliers}")

    def _save_to_json(self, data: Dict, filename: str):
        """Save data to JSON file."""
        self._ensure_log_directory()
        filepath = os.path.join(LOG_DIRECTORY, filename)
        
        try:
            # Load existing data if file exists
            existing_data = []
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = []
            
            # Append new data
            existing_data.append(data)
            
            # Save back to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")

    def _ensure_log_directory(self):
        """Ensure the log directory exists."""
        if not os.path.exists(LOG_DIRECTORY):
            os.makedirs(LOG_DIRECTORY)


def main():
    """Main function to run the sentiment bot."""
    bot = SentimentBot()
    bot.run()


if __name__ == "__main__":
    """Run the bot."""
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Critical error: {e}") 