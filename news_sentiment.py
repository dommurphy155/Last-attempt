import requests
import time
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import NEWS_SOURCES, SENTIMENT_MODELS, HUGGINGFACE_API_KEY, VOLATILITY_KEYWORDS
from utils import sanitize_text, extract_currency_pairs, log_error, log_action

logger = logging.getLogger(__name__)

class NewsSentimentAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.sentiment_models = {}
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.last_scrape_time = None
        self.scraped_articles = set()
        
        # Initialize sentiment models
        self._initialize_sentiment_models()
    
    def _initialize_sentiment_models(self):
        """Initialize sentiment analysis models"""
        try:
            # Try to load models from Hugging Face
            if HUGGINGFACE_API_KEY:
                for model_name in SENTIMENT_MODELS[:3]:  # Use first 3 models
                    try:
                        tokenizer = AutoTokenizer.from_pretrained(model_name)
                        model = AutoModelForSequenceClassification.from_pretrained(model_name)
                        self.sentiment_models[model_name] = pipeline(
                            "sentiment-analysis",
                            model=model,
                            tokenizer=tokenizer
                        )
                        logger.info(f"Loaded sentiment model: {model_name}")
                    except Exception as e:
                        logger.warning(f"Failed to load model {model_name}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error initializing sentiment models: {e}")
    
    def scrape_news_sources(self) -> List[Dict[str, Any]]:
        """Scrape news from all sources"""
        articles = []
        
        for source_url in NEWS_SOURCES:
            try:
                source_articles = self._scrape_source(source_url)
                articles.extend(source_articles)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                log_error(f"Failed to scrape {source_url}", {"error": str(e)})
                continue
        
        # Remove duplicates and filter recent articles
        unique_articles = self._deduplicate_articles(articles)
        return unique_articles
    
    def _scrape_source(self, url: str) -> List[Dict[str, Any]]:
        """Scrape articles from a specific source"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Generic article extraction
            article_elements = soup.find_all(['article', 'div', 'li'], class_=re.compile(r'article|news|post|item'))
            
            for element in article_elements[:10]:  # Limit to 10 articles per source
                try:
                    # Extract title
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
                    title = title_elem.get_text().strip() if title_elem else ""
                    
                    # Extract content
                    content_elem = element.find(['p', 'div', 'span'])
                    content = content_elem.get_text().strip() if content_elem else ""
                    
                    # Extract link
                    link_elem = element.find('a')
                    link = link_elem.get('href') if link_elem else ""
                    
                    if title and len(title) > 10:
                        article = {
                            "title": sanitize_text(title),
                            "content": sanitize_text(content),
                            "link": link,
                            "source": url,
                            "timestamp": datetime.now().isoformat()
                        }
                        articles.append(article)
                
                except Exception as e:
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return []
    
    def _deduplicate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title = article.get("title", "").lower()
            title_hash = hash(title[:50])  # Use first 50 chars as hash
            
            if title_hash not in seen_titles and title_hash not in self.scraped_articles:
                seen_titles.add(title_hash)
                self.scraped_articles.add(title_hash)
                unique_articles.append(article)
        
        return unique_articles
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using multiple models"""
        if not text or len(text) < 10:
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.0}
        
        # Clean and prepare text
        clean_text = sanitize_text(text)
        if len(clean_text) < 10:
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.0}
        
        # Use multiple sentiment analysis methods
        results = []
        
        # 1. VADER Sentiment
        try:
            vader_scores = self.vader_analyzer.polarity_scores(clean_text)
            vader_compound = vader_scores['compound']
            results.append({
                "method": "vader",
                "score": vader_compound,
                "sentiment": "positive" if vader_compound > 0.05 else "negative" if vader_compound < -0.05 else "neutral"
            })
        except Exception as e:
            logger.error(f"VADER sentiment error: {e}")
        
        # 2. TextBlob
        try:
            blob = TextBlob(clean_text)
            textblob_score = blob.sentiment.polarity
            results.append({
                "method": "textblob",
                "score": textblob_score,
                "sentiment": "positive" if textblob_score > 0.1 else "negative" if textblob_score < -0.1 else "neutral"
            })
        except Exception as e:
            logger.error(f"TextBlob sentiment error: {e}")
        
        # 3. Hugging Face Models
        for model_name, model in self.sentiment_models.items():
            try:
                # Truncate text if too long
                truncated_text = clean_text[:512] if len(clean_text) > 512 else clean_text
                result = model(truncated_text)
                
                if isinstance(result, list) and len(result) > 0:
                    result = result[0]
                
                if 'label' in result and 'score' in result:
                    label = result['label'].lower()
                    score = result['score']
                    
                    # Map labels to sentiment
                    if 'positive' in label or 'bullish' in label:
                        sentiment = "positive"
                    elif 'negative' in label or 'bearish' in label:
                        sentiment = "negative"
                    else:
                        sentiment = "neutral"
                    
                    results.append({
                        "method": model_name,
                        "score": score if sentiment == "positive" else -score,
                        "sentiment": sentiment
                    })
            
            except Exception as e:
                logger.error(f"Hugging Face model {model_name} error: {e}")
                continue
        
        # Combine results
        if not results:
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.0}
        
        # Calculate weighted average
        total_score = 0.0
        total_weight = 0.0
        
        for result in results:
            weight = 1.0
            if result["method"] == "vader":
                weight = 0.4
            elif result["method"] == "textblob":
                weight = 0.3
            else:
                weight = 0.3
            
            total_score += result["score"] * weight
            total_weight += weight
        
        if total_weight > 0:
            final_score = total_score / total_weight
            final_sentiment = "positive" if final_score > 0.1 else "negative" if final_score < -0.1 else "neutral"
            confidence = min(abs(final_score), 1.0)
        else:
            final_score = 0.0
            final_sentiment = "neutral"
            confidence = 0.0
        
        return {
            "sentiment": final_sentiment,
            "score": final_score,
            "confidence": confidence,
            "methods_used": len(results)
        }
    
    def detect_volatility_keywords(self, text: str) -> Dict[str, Any]:
        """Detect volatility-inducing keywords"""
        text_lower = text.lower()
        found_keywords = []
        volatility_score = 0.0
        
        for keyword in VOLATILITY_KEYWORDS:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
                volatility_score += 0.1
        
        return {
            "keywords_found": found_keywords,
            "volatility_score": min(volatility_score, 1.0),
            "has_volatility": len(found_keywords) > 0
        }
    
    def extract_forex_impact(self, text: str) -> Dict[str, Any]:
        """Extract forex-specific impact from text"""
        currency_pairs = extract_currency_pairs(text)
        
        # Look for specific forex terms
        forex_terms = [
            "forex", "currency", "exchange rate", "pip", "spread",
            "central bank", "interest rate", "inflation", "gdp",
            "employment", "trade balance", "current account"
        ]
        
        found_terms = []
        for term in forex_terms:
            if term.lower() in text.lower():
                found_terms.append(term)
        
        return {
            "currency_pairs": currency_pairs,
            "forex_terms": found_terms,
            "forex_relevance": len(found_terms) / len(forex_terms)
        }
    
    def analyze_news_sentiment(self) -> Dict[str, Any]:
        """Main method to analyze news sentiment"""
        try:
            log_action("Starting news sentiment analysis")
            
            # Scrape news articles
            articles = self.scrape_news_sources()
            if not articles:
                return {"sentiment": "neutral", "score": 0.0, "confidence": 0.0, "articles_analyzed": 0}
            
            # Analyze each article
            sentiment_scores = []
            volatility_scores = []
            forex_impacts = []
            
            for article in articles:
                # Combine title and content
                full_text = f"{article.get('title', '')} {article.get('content', '')}"
                
                # Analyze sentiment
                sentiment_result = self.analyze_sentiment(full_text)
                sentiment_scores.append(sentiment_result["score"])
                
                # Detect volatility
                volatility_result = self.detect_volatility_keywords(full_text)
                volatility_scores.append(volatility_result["volatility_score"])
                
                # Extract forex impact
                forex_result = self.extract_forex_impact(full_text)
                forex_impacts.append(forex_result)
            
            # Calculate aggregate scores
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                sentiment_confidence = min(len(sentiment_scores) / 10, 1.0)  # More articles = higher confidence
            else:
                avg_sentiment = 0.0
                sentiment_confidence = 0.0
            
            if volatility_scores:
                avg_volatility = sum(volatility_scores) / len(volatility_scores)
            else:
                avg_volatility = 0.0
            
            # Determine overall sentiment
            if avg_sentiment > 0.1:
                overall_sentiment = "positive"
            elif avg_sentiment < -0.1:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
            
            # Collect all currency pairs mentioned
            all_currency_pairs = set()
            for impact in forex_impacts:
                all_currency_pairs.update(impact.get("currency_pairs", []))
            
            result = {
                "sentiment": overall_sentiment,
                "score": avg_sentiment,
                "confidence": sentiment_confidence,
                "volatility_score": avg_volatility,
                "articles_analyzed": len(articles),
                "currency_pairs_mentioned": list(all_currency_pairs),
                "timestamp": datetime.now().isoformat()
            }
            
            log_action("Completed news sentiment analysis", result)
            return result
            
        except Exception as e:
            log_error("News sentiment analysis failed", {"error": str(e)})
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.0, "articles_analyzed": 0}
    
    def get_sentiment_summary(self) -> str:
        """Get a human-readable sentiment summary"""
        try:
            analysis = self.analyze_news_sentiment()
            
            sentiment_emoji = {
                "positive": "📈",
                "negative": "📉",
                "neutral": "➡️"
            }
            
            emoji = sentiment_emoji.get(analysis["sentiment"], "➡️")
            
            summary = f"{emoji} News Sentiment: {analysis['sentiment'].upper()}\n"
            summary += f"Score: {analysis['score']:.3f}\n"
            summary += f"Confidence: {analysis['confidence']:.1%}\n"
            summary += f"Volatility: {analysis['volatility_score']:.1%}\n"
            summary += f"Articles Analyzed: {analysis['articles_analyzed']}\n"
            
            if analysis.get("currency_pairs_mentioned"):
                summary += f"Pairs Mentioned: {', '.join(analysis['currency_pairs_mentioned'])}"
            
            return summary
            
        except Exception as e:
            return f"❌ Sentiment Analysis Error: {str(e)}"
    
    def should_avoid_trading(self) -> bool:
        """Check if trading should be avoided due to news"""
        try:
            analysis = self.analyze_news_sentiment()
            
            # Avoid trading if:
            # 1. High volatility score (> 0.7)
            # 2. Very negative sentiment (< -0.3)
            # 3. High confidence in extreme sentiment
            
            if analysis["volatility_score"] > 0.7:
                return True
            
            if analysis["sentiment"] == "negative" and analysis["score"] < -0.3:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking trading avoidance: {e}")
            return False