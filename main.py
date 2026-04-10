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

# 최신 모델
model = genai.GenerativeModel("gemini-2.5-flash")

# 🔥 키워드 설정
KEYWORDS = ["관세", "트럼프", "수출"]
query = "+OR+".join(KEYWORDS)

RSS_URL = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"

feed = feedparser.parse(RSS_URL)

articles_data = []
titles = set()

print(f"--- 뉴스 수집 시작 (키워드: {KEYWORDS}) ---")

for entry in feed.entries[:15]:
    title = entry.title
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

    if len(text) < 300:
        text = entry.summary

    if len(text) > 100:
        articles_data.append({
            "title": title,
            "content": text[:1000]
        })
        print(f"✅ 수집 완료: {title[:30]}...")

# 🔥 텍스트 합치기
combined_text = ""
for i, item in enumerate(articles_data, 1):
    combined_text += f"[기사{i}]\n제목:{item['title']}\n내용:{item['content']}\n\n"

# 🔥 프롬프트
prompt = f"""
다음 뉴스들을 기반으로 핵심 인사이트를 요약하라.

[출력 형식]

📅 오늘의 뉴스 인사이트 ({', '.join(KEYWORDS)})

1. 한 줄 요약
- 전체 흐름 한 문장

2. 핵심 이슈
- 3~5개 bullet point

3. 시사점
- 중요한 영향과 향후 변화

[스타일]
- 짧고 명확
- 불필요한 기호 사용 금지

뉴스:
{combined_text}
"""

# 🔥 Gemini 분석
if not articles_data:
    final_message = "❌ 뉴스 없음"
else:
    try:
        print("--- Gemini 분석 중... ---")
        response = model.generate_content(prompt)
        final_message = response.text
    except Exception as e:
        print("Gemini Error:", e)
        final_message = "❌ 요약 실패"

# 🔥 텔레그램 전송 (핵심 수정)
try:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": final_message
        # ❌ parse_mode 제거
    }

    res = requests.post(url, json=payload)

    if res.status_code == 200:
        print("✅ 전송 성공")
    else:
        print("❌ 전송 실패:", res.text)

except Exception as e:
    print("Telegram Error:", e)
