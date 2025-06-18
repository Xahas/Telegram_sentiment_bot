#!/usr/bin/env python3
"""
Helper script to get Chat ID for monitoring.
Run this script, then send a message in your target chat to see the Chat ID.
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatIDFinder:
    """Simple bot to help find chat IDs."""
    
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Add message handler
        message_handler = MessageHandler(filters.ALL, self.handle_message)
        self.application.add_handler(message_handler)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle any message and show chat info."""
        try:
            message = update.message
            if not message:
                return
            
            chat_type = message.chat.type
            chat_id = message.chat.id
            chat_title = getattr(message.chat, 'title', 'N/A')
            user_name = message.from_user.first_name if message.from_user else 'Unknown'
            
            print(f"\n📨 New message received!")
            print(f"💬 Chat ID: {chat_id}")
            print(f"🏷️  Chat Type: {chat_type}")
            print(f"📛 Chat Title: {chat_title}")
            print(f"👤 From: {user_name}")
            print(f"📝 Message: {message.text[:50]}..." if message.text else "No text")
            print("-" * 50)
            
            # Show setup instruction
            if chat_type in ['group', 'supergroup']:
                print(f"✅ To monitor this chat, update config.py:")
                print(f"   MONITOR_CHAT_ID = {chat_id}")
                print("-" * 50)
                
        except Exception as e:
            logger.error(f"Error: {e}")
    
    def run(self):
        """Run the chat ID finder."""
        print("\n" + "="*60)
        print("🔍 TELEGRAM CHAT ID FINDER")
        print("="*60)
        print("This bot will show Chat IDs for any chat it receives messages from.")
        print("Steps:")
        print("1. Add this bot to your target chat/group")
        print("2. Send any message in that chat")  
        print("3. Copy the Chat ID and update config.py")
        print("4. Press Ctrl+C to stop this script")
        print("="*60)
        
        try:
            self.application.run_polling(
                drop_pending_updates=True
            )
        except KeyboardInterrupt:
            print("\n👋 Chat ID finder stopped")


def main():
    """Main function."""
    finder = ChatIDFinder()
    finder.run()


if __name__ == "__main__":
    main() 