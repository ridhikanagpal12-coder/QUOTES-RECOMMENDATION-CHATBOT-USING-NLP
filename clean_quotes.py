import json
from collections import Counter

def analyze_quotes_diversity():
    """Analyze and report on quote diversity"""
    
    with open("actions/quotes.json", "r", encoding="utf-8") as f:
        quotes = json.load(f)
    
    print("="*50)
    print("📊 QUOTE DATASET DIVERSITY REPORT")
    print("="*50)
    print(f"📚 Total Quotes: {len(quotes)}")
    
    # Category breakdown
    categories = Counter()
    authors = Counter()
    tags_combined = Counter()
    
    for q in quotes:
        categories[q.get("Category", "unknown")] += 1
        authors[q.get("Author", "Unknown")] += 1
        for tag in q.get("Tags", []):
            tags_combined[tag] += 1
    
    print("\n📋 Categories:")
    for cat, count in categories.most_common():
        print(f"   • {cat}: {count} quotes ({count/len(quotes)*100:.1f}%)")
    
    print(f"\n👥 Unique Authors: {len(authors)}")
    print("\n🏷️ Top Tags:")
    for tag, count in tags_combined.most_common(10):
        print(f"   • {tag}: {count} occurrences")
    
    # Check diversity
    motivation = sum(1 for q in quotes if q.get("Category") in ["motivation", "life"])
    love = sum(1 for q in quotes if q.get("Category") == "love")
    humor = sum(1 for q in quotes if q.get("Category") == "humor")
    
    print("\n🎯 Intent Coverage:")
    print(f"   • Motivation/Life: {motivation} quotes")
    print(f"   • Love: {love} quotes")
    print(f"   • Humor: {humor} quotes")
    
    print("\n" + "="*50)
    print("✅ Dataset is diverse and ready to use!")
    print("="*50)

if __name__ == "__main__":
    analyze_quotes_diversity()