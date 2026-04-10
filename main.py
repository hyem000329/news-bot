import os
import feedparser
import requests
from newspaper import Article
import google.generativeai as genai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

RSS_URL = "https://news.google.com/rss/search?q=AI+OR+관세+OR+반도체&hl=ko&gl=KR&ceid=KR:ko"

feed = feedparser.parse(RSS_URL)

articles_text = []

for entry in feed.entries[:5]:
    # 🔥 핵심: 실제 링크 추출
    link = entry.link

    # Google redirect 우회
    if "news.google.com" in link:
        link = entry.link.split("&url=")[-1] if "&url=" in entry.link else entry.link

    print("URL:", link)

    text = ""

    try:
        article = Article(link)
        article.download()
        article.parse()
        text = article.text
    except:
        pass

    # 🔥 fallback (이게 핵심)
    if len(text) < 300:
        text = entry.summary

    print("TEXT LENGTH:", len(text))

    if len(text) < 100:
        continue

    articles_text.append(text[:1500])

# 🔥 데이터 없을 경우
if not articles_text:
    final_message = "❌ 뉴스 데이터를 가져오지 못했습니다."
else:
    combined_text = "\n\n".join(articles_text)

    prompt = f"""
    아래 뉴스들을 종합해서 하나의 보고서로 정리해줘.

    1. 전체 흐름 요약 (3줄)
    2. 핵심 이슈 3개
    3. 키워드 5개

    {combined_text}
    """

    try:
        response = model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        print("Gemini Error:", e)
        summary = "요약 실패"

    final_message = f"📰 오늘의 뉴스 요약\n\n{summary}"

res = requests.get(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    params={"chat_id": CHAT_ID, "text": final_message}
)

print(res.text)
print("완료")
