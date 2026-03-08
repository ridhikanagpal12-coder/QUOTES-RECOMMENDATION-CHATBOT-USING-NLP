import json
import random
import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# ========== QUOTE MANAGER ==========
class QuoteManager:
    """Quote management system"""
    
    def __init__(self, quotes_path="quotes.json"):
        self.quotes = []
        self.quotes_by_category = {}
        self.load_quotes(quotes_path)
        
    def load_quotes(self, path):
        """Load and index quotes"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                quotes = json.load(f)
        except FileNotFoundError:
            # Try alternative path
            try:
                with open("actions/quotes.json", 'r', encoding='utf-8') as f:
                    quotes = json.load(f)
            except:
                quotes = self.get_fallback_quotes()
        
        # Deduplicate
        seen = set()
        for q in quotes:
            quote_text = q.get("Quote", "").strip()
            if not quote_text or len(quote_text) < 5 or quote_text.lower() in seen:
                continue
            
            seen.add(quote_text.lower())
            
            cleaned = {
                "Quote": quote_text,
                "Author": q.get("Author", "Unknown"),
                "Category": q.get("Category", "uncategorized").lower(),
                "Tags": [t.lower() for t in q.get("Tags", [])]
            }
            
            self.quotes.append(cleaned)
            
            # Index by category
            cat = cleaned["Category"]
            if cat not in self.quotes_by_category:
                self.quotes_by_category[cat] = []
            self.quotes_by_category[cat].append(cleaned)
        
        print(f"✅ Loaded {len(self.quotes)} unique quotes")
        
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
        ]
    
    def get_quote(self, category=None, exclude_quotes=None):
        """Get quote with filtering"""
        if category and category in self.quotes_by_category:
            candidates = self.quotes_by_category[category]
        else:
            candidates = self.quotes
        
        # Exclude recent quotes
        if exclude_quotes and candidates:
            candidates = [q for q in candidates 
                         if q["Quote"] not in exclude_quotes[-5:]]
        
        if not candidates:
            candidates = self.quotes
        
        return random.choice(candidates) if candidates else random.choice(self.quotes)
    
    def get_quotes_by_emotion(self, emotion, exclude_quotes=None):
        """Get quotes based on emotion"""
        emotion_map = {
            "happy": ["humor", "motivation"],
            "sad": ["love", "life"],
            "stressed": ["motivation", "life"],
            "down": ["motivation", "love"],
            "low": ["motivation", "love"],
            "lonely": ["love", "life"],
            "tired": ["motivation", "humor"],
            "anxious": ["life", "love"]
        }
        
        # Find matching emotion
        categories = []
        emotion_lower = emotion.lower()
        for key, cats in emotion_map.items():
            if key in emotion_lower:
                categories.extend(cats)
        
        if not categories:
            categories = ["motivation"]
        
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

# ========== SENTIMENT ANALYSIS ==========
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
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    return "neutral"

# ========== INITIALIZE ==========
quote_manager = QuoteManager()

# ========== CUSTOM ACTIONS ==========
class ActionSendQuote(Action):
    """Send quote based on intent"""
    
    def name(self) -> Text:
        return "action_send_quote"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_message = tracker.latest_message.get("text", "")
        intent = tracker.latest_message.get("intent", {}).get("name", "")
        
        # Get sentiment
        sentiment = get_sentiment(user_message)
        
        # Get existing history
        history = tracker.get_slot("quote_history") or []
        if not isinstance(history, list):
            history = []
        
        # Map intent to category
        category_map = {
            "motivation": "motivation",
            "love": "love",
            "humor": "humor"
        }
        
        category = category_map.get(intent)
        
        # Get quote
        quote = quote_manager.get_quote(
            category=category,
            exclude_quotes=history
        )
        
        # Format message with sentiment
        if sentiment == "negative":
            prefix = random.choice([
                "I hear you. Here's something uplifting:",
                "That sounds tough. This might help:",
                "Sending positive vibes your way:"
            ])
        elif sentiment == "positive":
            prefix = random.choice([
                "Awesome! Here's a quote to match your energy:",
                "Love that positivity! Here you go:",
                "Perfect mood for this quote:"
            ])
        else:
            prefix = random.choice([
                "Here's a quote for you:",
                "Check this out:",
                "This might inspire you:"
            ])
        
        message = f"{prefix}\n\n\"{quote['Quote']}\"\n— {quote['Author']}"
        
        dispatcher.utter_message(text=message)
        
        # Update history
        history.append(quote["Quote"])
        if len(history) > 10:
            history = history[-10:]
        
        return [SlotSet("last_quote", quote["Quote"]),
                SlotSet("last_category", quote["Category"]),
                SlotSet("quote_history", history)]

class ActionAnotherQuote(Action):
    """Send another quote"""
    
    def name(self) -> Text:
        return "action_another_quote"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get last category and history
        last_category = tracker.get_slot("last_category")
        history = tracker.get_slot("quote_history") or []
        
        if not isinstance(history, list):
            history = []
        
        # Get quote
        quote = quote_manager.get_quote(
            category=last_category,
            exclude_quotes=history
        )
        
        message = f"Here's another one:\n\n\"{quote['Quote']}\"\n— {quote['Author']}"
        
        dispatcher.utter_message(text=message)
        
        # Update history
        history.append(quote["Quote"])
        if len(history) > 10:
            history = history[-10:]
        
        return [SlotSet("last_quote", quote["Quote"]),
                SlotSet("quote_history", history)]

class ActionSendQuoteByEmotion(Action):
    """Send quote based on detected emotion"""
    
    def name(self) -> Text:
        return "action_send_quote_by_emotion"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_message = tracker.latest_message.get("text", "")
        history = tracker.get_slot("quote_history") or []
        
        if not isinstance(history, list):
            history = []
        
        # Get quote by emotion
        quote = quote_manager.get_quotes_by_emotion(
            user_message,
            exclude_quotes=history
        )
        
        prefix = "Here's a quote for your mood:"
        
        message = f"{prefix}\n\n\"{quote['Quote']}\"\n— {quote['Author']}"
        
        dispatcher.utter_message(text=message)
        
        # Update history
        history.append(quote["Quote"])
        if len(history) > 10:
            history = history[-10:]
        
        return [SlotSet("quote_history", history)]

# Import SlotSet
from rasa_sdk.events import SlotSet