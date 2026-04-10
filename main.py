import os
import feedparser
import requests
from newspaper import Article
import google.generativeai as genai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 👉 넓게 가져오기 (필터 없이)
RSS_URL = "https://news.google.com/rss/search?q=AI+OR+관세+OR+반도체&hl=ko&gl=KR&ceid=KR:ko"

feed = feedparser.parse(RSS_URL)

articles_text = []

# 🔹 여러 기사 수집
for entry in feed.entries[:5]:
    url = entry.link

    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text[:1000]

        if len(text) > 200:
            articles_text.append(text)

    except:
        continue

# 🔹 전체 텍스트 합치기
combined_text = "\n\n".join(articles_text)

# 🔹 Gemini로 전체 요약
prompt = f"""
다음 뉴스 여러 개를 읽고,
중요한 흐름과 핵심 내용을 정리해서 요약해줘.

- 전체 트렌드
- 중요한 이슈 3~5개
- 핵심 키워드

{combined_text}
"""

response = model.generate_content(prompt)
summary = response.text

# 🔹 텔레그램 전송 (1번만)
message = f"📰 오늘의 뉴스 요약\n\n{summary}"

res = requests.get(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    params={"chat_id": CHAT_ID, "text": message}
)

print(res.text)
