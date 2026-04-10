import os
import feedparser
import requests
from newspaper import Article
import google.generativeai as genai

# 🔐 환경변수
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

RSS_URL = "https://news.google.com/rss/search?q=AI+OR+관세+OR+반도체&hl=ko&gl=KR&ceid=KR:ko"

# 👉 관심 키워드 (자유 수정)
KEYWORDS = ["AI", "반도체", "관세", "투자"]

feed = feedparser.parse(RSS_URL)

for entry in feed.entries[:5]:
    title = entry.title
    url = entry.link

    # 🔍 키워드 필터
    if not any(k.lower() in title.lower() for k in KEYWORDS):
        continue

    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text[:2000]
    except:
        text = ""

    # 🤖 Gemini 요약
    try:
        prompt = f"""
        다음 뉴스 내용을 한국어로 3줄 요약하고,
        핵심 키워드 3개 뽑아줘:

        {text}
        """

        response = model.generate_content(prompt)
        summary = response.text

    except Exception as e:
        summary = "요약 실패"

    message = f"📰 {title}\n\n{summary}\n\n{url}"

    res = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": message}
    )

    print(res.text)

print("완료")
