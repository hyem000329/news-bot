import os
import feedparser
import requests
from newspaper import Article

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_URL = "https://news.google.com/rss/search?q=AI"

feed = feedparser.parse(RSS_URL)

for entry in feed.entries[:3]:
    url = entry.link

    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text[:200]
    except:
        text = "본문 추출 실패"

    message = f"📰 {entry.title}\n\n{text}\n\n{url}"

    res = requests.get(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    params={"chat_id": CHAT_ID, "text": message}
)

print(res.text)

print("완료")
