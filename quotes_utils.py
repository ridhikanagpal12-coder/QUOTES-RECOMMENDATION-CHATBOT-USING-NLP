import json
import random
import re
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional

class QuoteManager:
    """Advanced quote management system"""
    
    def __init__(self, quotes_path="actions/quotes.json"):
        self.quotes = []
        self.quotes_by_category = defaultdict(list)
        self.quotes_by_author = defaultdict(list)
        self.quotes_by_tag = defaultdict(list)
        self.author_popularity = Counter()
        self.category_popularity = Counter()
        self.session_history = []
        
        self.load_quotes(quotes_path)
        
    def load_quotes(self, path):
        """Load and index quotes"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                quotes = json.load(f)
        except:
            # Fallback quotes if file not found
            quotes = self.get_fallback_quotes()
        
        # Deduplicate
        seen = set()
        for q in quotes:
            quote_text = q.get("Quote", "").strip()
            if not quote_text or len(quote_text) < 5 or quote_text.lower() in seen:
                continue
            
            seen.add(quote_text.lower())
            
            # Clean and enrich
            cleaned = {
                "Quote": quote_text,
                "Author": q.get("Author", "Unknown"),
                "Category": q.get("Category", "uncategorized").lower(),
                "Tags": [t.lower() for t in q.get("Tags", [])],
                "Length": len(quote_text.split()),
                "Added": q.get("Added", "original")
            }
            
            self.quotes.append(cleaned)
            
            # Index
            self.quotes_by_category[cleaned["Category"]].append(cleaned)
            self.quotes_by_author[cleaned["Author"]].append(cleaned)
            for tag in cleaned["Tags"]:
                self.quotes_by_tag[tag].append(cleaned)
        
        print(f"✅ Loaded {len(self.quotes)} unique quotes")
        print(f"📊 Categories: {list(self.quotes_by_category.keys())}")
        
    def get_fallback_quotes(self):
        """Fallback quotes if file not found"""
        return [
            {"Quote": "The only way to do great work is to love what you do.", 
             "Author": "Steve Jobs", "Category": "motivation", "Tags": ["work", "passion"]},
            {"Quote": "Life is what happens when you're busy making other plans.", 
             "Author": "John Lennon", "Category": "life", "Tags": ["wisdom", "present"]},
            {"Quote": "You only live once, but if you do it right, once is enough.", 
             "Author": "Mae West", "Category": "humor", "Tags": ["funny", "life"]},
            {"Quote": "I love you without knowing how, or when, or from where.", 
             "Author": "Pablo Neruda", "Category": "love", "Tags": ["romantic"]},
            {"Quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.", 
             "Author": "Winston Churchill", "Category": "motivation", "Tags": ["success", "courage"]}
        ]
    
    def get_quote(self, category=None, author=None, tags=None, exclude_quotes=None):
        """Get quote with advanced filtering"""
        
        candidates = self.quotes.copy()
        
        # Apply filters
        if category:
            category = category.lower()
            if category in self.quotes_by_category:
                candidates = self.quotes_by_category[category]
        
        if author:
            author = author.lower()
            candidates = [q for q in candidates 
                         if q["Author"].lower() == author]
        
        if tags:
            tags = [t.lower() for t in tags]
            candidates = [q for q in candidates 
                         if any(t in q["Tags"] for t in tags)]
        
        # Exclude recent quotes
        if exclude_quotes and candidates:
            candidates = [q for q in candidates 
                         if q["Quote"] not in exclude_quotes[-10:]]
        
        if not candidates:
            candidates = self.quotes
        
        # Update popularity
        quote = random.choice(candidates)
        self.author_popularity[quote["Author"]] += 1
        self.category_popularity[quote["Category"]] += 1
        self.session_history.append(quote["Quote"])
        
        return quote
    
    def get_quotes_by_emotion(self, emotion, exclude_quotes=None):
        """Get quotes based on emotion"""
        
        emotion_map = {
            "happy": ["humor", "motivation", "success"],
            "sad": ["inspiration", "love", "life"],
            "stressed": ["motivation", "inspiration", "wisdom"],
            "down": ["motivation", "inspiration", "life"],
            "low": ["motivation", "inspiration", "love"],
            "angry": ["wisdom", "inspiration", "life"],
            "lonely": ["love", "inspiration", "life"],
            "tired": ["motivation", "humor", "success"],
            "excited": ["motivation", "success", "humor"],
            "anxious": ["inspiration", "wisdom", "love"],
            "romantic": ["love"],
            "confused": ["wisdom", "inspiration"],
            "grateful": ["life", "inspiration"]
        }
        
        # Find matching emotion
        categories = []
        emotion_lower = emotion.lower()
        for key, cats in emotion_map.items():
            if key in emotion_lower or emotion_lower in key:
                categories.extend(cats)
        
        if not categories:
            categories = ["motivation", "inspiration"]
        
        # Get quotes from these categories
        candidates = []
        for cat in categories:
            if cat in self.quotes_by_category:
                candidates.extend(self.quotes_by_category[cat])
        
        if not candidates:
            candidates = self.quotes
        
        # Exclude recent
        if exclude_quotes and candidates:
            candidates = [q for q in candidates 
                         if q["Quote"] not in exclude_quotes[-5:]]
        
        return random.choice(candidates) if candidates else random.choice(self.quotes)
    
    def search_by_author(self, author_name):
        """Search quotes by author"""
        author_name = author_name.lower()
        results = []
        
        for author, quotes in self.quotes_by_author.items():
            if author_name in author.lower():
                results.extend(quotes)
        
        return results[:5]  # Return top 5
    
    def search_by_topic(self, topic):
        """Search quotes by topic/tag"""
        topic = topic.lower()
        results = []
        
        # Search in tags
        for tag, quotes in self.quotes_by_tag.items():
            if topic in tag:
                results.extend(quotes)
        
        # Search in quote text
        if not results:
            for q in self.quotes:
                if topic in q["Quote"].lower():
                    results.append(q)
        
        return results[:5]
    
    def get_popular_quotes(self, limit=5):
        """Get most popular quotes by request count"""
        # This would need tracking in a real DB
        popular = sorted(self.quotes, 
                        key=lambda q: self.author_popularity.get(q["Author"], 0),
                        reverse=True)
        return popular[:limit]
    
    def get_daily_quote(self):
        """Get quote of the day (deterministic but varied)"""
        import hashlib
        import datetime
        
        # Use date to seed
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        seed = int(hashlib.md5(date_str.encode()).hexdigest(), 16) % len(self.quotes)
        
        return self.quotes[seed]

# Global instance
quote_manager = QuoteManager()

def get_sentiment(text):
    """Simple sentiment analysis"""
    positive_words = {
        'happy', 'great', 'good', 'awesome', 'love', 'joy', 'excited', 
        'fantastic', 'amazing', 'wonderful', 'perfect', 'beautiful',
        'glad', 'delighted', 'pleased', 'grateful', 'thankful'
    }
    negative_words = {
        'sad', 'bad', 'upset', 'angry', 'depressed', 'lonely', 'stressed',
        'terrible', 'awful', 'horrible', 'down', 'low', 'unhappy',
        'miserable', 'heartbroken', 'devastated', 'hopeless'
    }
    
    words = set(re.findall(r'\w+', text.lower()))
    pos_count = len(words.intersection(positive_words))
    neg_count = len(words.intersection(negative_words))
    
    if pos_count > neg_count:
        return "positive", pos_count - neg_count
    elif neg_count > pos_count:
        return "negative", neg_count - pos_count
    return "neutral", 0