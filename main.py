import os
import feedparser
import requests
from newspaper import Article

# 🔐 환경변수 (GitHub Secrets에서 가져옴)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_URL = "https://news.google.com/rss/search?q=AI"

feed = feedparser.parse(RSS_URL)

for entry in feed.entries[:3]:
    url = entry.link

    article = Article(url)
    article.download()
    article.parse()

    text = article.text[:1000]

    message = f"📰 {entry.title}\n\n{text[:200]}...\n\n{url}"

    requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": message}
    )

print("완료")
