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

# 🔥 공백 → + 로 변경 (중요)
RSS_URL = "https://news.google.com/rss/search?q=AI+OR+관세+OR+반도체&hl=ko&gl=KR&ceid=KR:ko"

feed = feedparser.parse(RSS_URL)

articles_text = []

for entry in feed.entries[:5]:
    url = entry.link

    # 🔥 Google 뉴스 링크 보정 (핵심)
    if "news.google.com" in url:
        url = entry.get("source", {}).get("href", url)

    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text
    except:
        text = ""

    # 🔥 fallback (본문 없을 때)
    if len(text) < 200:
        text = entry.summary

    # 너무 짧으면 버림
    if len(text) < 100:
        continue

    print("TEXT LENGTH:", len(text))  # 디버깅용

    articles_text.append(text[:1000])

# 🔥 기사 하나도 없을 경우 대비
if len(articles_text) == 0:
    final_message = "❌ 뉴스 본문을 가져오지 못했습니다."
else:
    combined_text = "\n\n".join(articles_text)

    prompt = f"""
    다음 뉴스들을 종합해서 하나의 보고서처럼 정리해줘.

    [요구사항]
    1. 전체 흐름 요약 (3~5줄)
    2. 핵심 이슈 3가지 (bullet point)
    3. 중요한 키워드 5개

    {combined_text}
    """

    try:
        response = model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        summary = "요약 실패"

    final_message = f"📰 오늘의 뉴스 요약\n\n{summary}"

# 🔥 텔레그램 전송 (한 번만)
res = requests.get(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    params={
        "chat_id": CHAT_ID,
        "text": final_message
    }
)

print(res.text)
print("완료")
