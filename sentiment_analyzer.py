#!/usr/bin/env python3
"""
Sentiment Analysis Module for Russian Text
Uses HuggingFace transformers to analyze sentiment in Russian messages.
Converts sentiment to a 1-10 scale where 1 is very negative and 10 is very positive.
"""

import logging
import re
import asyncio
from typing import Dict, Optional, Tuple
from datetime import datetime

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

from config import MODEL_NAME, SENTIMENT_SCALE_MIN, SENTIMENT_SCALE_MAX

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RussianSentimentAnalyzer:
    """
    Russian sentiment analyzer using HuggingFace transformers.
    Provides sentiment scores on a 1-10 scale for Russian text.
    """
    
    def __init__(self, model_name: str):
        """Initialize the Russian sentiment analyzer with specified model."""
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing sentiment analyzer with model: {model_name}")
        logger.info(f"Using device: {self.device}")
        
    def load_model(self):
        """Load the sentiment analysis model and tokenizer."""
        try:
            logger.info("Loading tokenizer and model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("✅ Model loaded successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis (Twitter format for this model)."""
        # Replace usernames and URLs as per model recommendations
        text = re.sub(r'@\w+', '@user', text)
        text = re.sub(r'http[s]?://\S+', 'http', text)
        
        # Basic cleanup
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = text.strip()
        
        return text
    
    def _convert_to_scale(self, probabilities: Dict[str, float]) -> float:
        """
        Convert model probabilities to 1-10 sentiment scale.
        This model outputs: Negative, Neutral, Positive
        """
        # Extract probabilities - this model uses these exact labels
        negative_prob = probabilities.get('LABEL_0', 0.0)  # Negative
        neutral_prob = probabilities.get('LABEL_1', 0.0)   # Neutral  
        positive_prob = probabilities.get('LABEL_2', 0.0)  # Positive
        
        # Calculate sentiment polarity (-1 to +1)
        polarity = positive_prob - negative_prob
        
        # Get the confidence (max probability)
        confidence = max(negative_prob, neutral_prob, positive_prob)
        
        # Convert to 1-10 scale with confidence-based adjustments
        if polarity < -0.1:  # Negative sentiment
            if confidence > 0.9:  # Very confident negative
                base_score = 1.0 + (polarity + 1) * 1.5  # Range: 1.0-2.5
            elif confidence > 0.7:  # Confident negative
                base_score = 1.5 + (polarity + 1) * 1.5  # Range: 1.5-3.0
            else:  # Less confident negative
                base_score = 2.5 + (polarity + 1) * 1.0  # Range: 2.5-3.5
        elif polarity > 0.1:  # Positive sentiment
            if confidence > 0.9:  # Very confident positive
                base_score = 8.5 + polarity * 1.5  # Range: 8.5-10.0
            elif confidence > 0.7:  # Confident positive
                base_score = 7.0 + polarity * 1.5  # Range: 7.0-8.5
            else:  # Less confident positive
                base_score = 6.5 + polarity * 0.5  # Range: 6.5-7.0
        else:  # Neutral sentiment
            # Fine-tune neutral range based on slight positive/negative tendencies
            base_score = 5.0 + polarity * 0.8  # Range: 4.2-5.8
            
            # Add slight variation based on confidence
            if confidence > 0.8:  # Very neutral
                base_score = 5.0
            else:  # Less certain neutral, add small variation
                base_score += (0.5 - confidence) * 0.6
        
        # Ensure we stay within bounds and add tiny random variation for granularity
        sentiment_score = max(1.0, min(10.0, base_score))
        
        # Add minimal random variation for more granular scoring
        variation = np.random.uniform(-0.05, 0.05)
        sentiment_score = max(1.0, min(10.0, sentiment_score + variation))
        
        return round(sentiment_score, 1)
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of given text.
        Returns (sentiment_score, sentiment_label)
        """
        if not text or not text.strip():
            return 5.0, "NEUTRAL"
        
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Tokenize
            inputs = self.tokenizer(
                processed_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            ).to(self.device)
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
                probabilities = probabilities.cpu().numpy()[0]
            
            # Create probability dictionary
            prob_dict = {
                'LABEL_0': float(probabilities[0]),  # Negative
                'LABEL_1': float(probabilities[1]),  # Neutral
                'LABEL_2': float(probabilities[2])   # Positive
            }
            
            # Convert to 1-10 scale
            sentiment_score = self._convert_to_scale(prob_dict)
            
            # Determine sentiment label
            if sentiment_score <= 3.5:
                sentiment_label = "NEGATIVE"
            elif sentiment_score >= 6.5:
                sentiment_label = "POSITIVE"
            else:
                sentiment_label = "NEUTRAL"
            
            return sentiment_score, sentiment_label
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 5.0, "NEUTRAL"
    
    def is_outlier(self, sentiment_score: float, low_threshold: float = 3.0, high_threshold: float = 7.5) -> bool:
        """Check if sentiment score is an outlier."""
        return sentiment_score <= low_threshold or sentiment_score >= high_threshold
    
    def get_sentiment_category(self, score: float) -> str:
        """Get human-readable sentiment category."""
        if score <= 2.0:
            return "Very Negative"
        elif score <= 4.0:
            return "Negative"
        elif score <= 6.0:
            return "Neutral"
        elif score <= 8.0:
            return "Positive"
        else:
            return "Very Positive"

# Async wrapper for compatibility
async def analyze_sentiment_async(analyzer: RussianSentimentAnalyzer, text: str) -> Tuple[float, str]:
    """Async wrapper for sentiment analysis."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, analyzer.analyze_sentiment, text)


# Global analyzer instance
analyzer = RussianSentimentAnalyzer(MODEL_NAME)


async def analyze_message_sentiment(text: str) -> Dict:
    """
    Convenience function to analyze sentiment of a single message.
    
    Args:
        text (str): Message text to analyze
        
    Returns:
        Dict: Sentiment analysis results
    """
    return await analyze_sentiment_async(analyzer, text)


async def init_sentiment_analyzer() -> bool:
    """
    Initialize the global sentiment analyzer.
    
    Returns:
        bool: True if initialization successful
    """
    return await analyzer.load_model()


if __name__ == "__main__":
    """Test the sentiment analyzer with sample Russian text."""
    
    async def test_analyzer():
        print("Testing Russian Sentiment Analyzer...")
        print("=" * 50)
        
        # Initialize
        success = await init_sentiment_analyzer()
        if not success:
            print("❌ Failed to initialize analyzer")
            return
        
        # Test messages in Russian
        test_messages = [
            "Это отличный день! Я очень счастлив!",  # Very positive
            "Мне грустно и плохо сегодня...",         # Negative
            "Обычный день, ничего особенного.",       # Neutral
            "Я в ярости! Это ужасно!",               # Very negative
            "Неплохо, но могло быть лучше.",         # Slightly negative/neutral
            "Потрясающе! Лучший день в жизни!",      # Very positive
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. Analyzing: '{message}'")
            result = await analyze_message_sentiment(message)
            
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   📊 Score: {result['score']}/10")
                print(f"   🏷️  Label: {result['label']}")
                print(f"   🎯 Confidence: {result['confidence']}")
                
                is_outlier = analyzer.is_outlier(result['score'])
                if is_outlier:
                    print(f"   ⚠️  Outlier detected")
    
    # Run test
    asyncio.run(test_analyzer()) 