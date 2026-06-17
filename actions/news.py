import feedparser

def get_india_news(limit=5):
    feed = feedparser.parse(
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    )

    headlines = []

    for article in feed.entries[:limit]:
        headlines.append(article.title)

    return headlines