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

# 🔥 최신 모델 (중요)
model = genai.GenerativeModel("gemini-2.5-flash")

# 🔥 키워드: 관세
RSS_URL = "https://news.google.com/rss/search?q=관세&hl=ko&gl=KR&ceid=KR:ko"

feed = feedparser.parse(RSS_URL)

articles_text = []
titles = set()

# 🔥 15개 뉴스 수집
for entry in feed.entries[:15]:
    title = entry.title

    # 중복 제거
    if title in titles:
        continue
    titles.add(title)

    url = entry.link

    text = ""

    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text
    except:
        pass

    # 🔥 fallback
    if len(text) < 300:
        text = entry.summary

    if len(text) < 100:
        continue

    print("TEXT LENGTH:", len(text))

    articles_text.append(text[:1200])

# 🔥 데이터 없을 경우
if not articles_text:
    final_message = "❌ 뉴스 데이터를 가져오지 못했습니다."
else:
    combined_text = "\n\n".join(articles_text)

    # 🔥 서비스형 프롬프트
    prompt = f"""
다음 뉴스들을 기반으로 간결한 뉴스 브리핑을 작성해라.

[출력 형식]

📰 오늘의 관세 뉴스 브리핑

1. 전체 흐름 (3줄 이내)
- 현재 상황을 한눈에 이해할 수 있게 요약

2. 핵심 이슈 (3~5개)
- bullet point로 짧고 명확하게
- 각 이슈는 한 줄 설명

3. 시사점
- 이 뉴스들이 의미하는 핵심 변화
- 앞으로 어떤 영향이 있을지
- 핵심만 간결하게

[스타일]
- 짧고 명확하게
- 불필요한 설명 금지
- 뉴스 앱처럼 읽기 쉽게

뉴스:
{combined_text}
"""

    try:
        response = model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        print("Gemini Error:", e)
        summary = "요약 실패"

    final_message = f"{summary}"

# 🔥 텔레그램 전송
res = requests.get(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    params={
        "chat_id": CHAT_ID,
        "text": final_message
    }
)

print(res.text)
print("완료")
