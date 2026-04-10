import os
import feedparser
import requests
from newspaper import Article
import google.generativeai as genai

# 🔐 1. 환경변수 설정
# 직접 입력 시: "YOUR_KEY" 형태로 작성
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)
# 무료 티어에서 가장 빠르고 효율적인 모델 (1.5 Flash 권장)
model = genai.GenerativeModel("gemini-1.5-flash")

# 🔥 2. 키워드 설정
KEYWORDS = ["관세", "트럼프", "수출"]
query = "+OR+".join(KEYWORDS)
RSS_URL = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"

# 🔍 3. 뉴스 수집 및 크롤링
feed = feedparser.parse(RSS_URL)
articles_data = []
titles = set()

print(f"--- 뉴스 수집 시작 (키워드: {KEYWORDS}) ---")

for entry in feed.entries[:15]:
    title = entry.title
    if title in titles: continue
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

    # 본문이 너무 짧으면 summary로 대체
    if len(text) < 300:
        text = entry.summary

    if len(text) > 100:
        # Gemini 입력 토큰 절약을 위해 기사당 길이를 제한
        articles_data.append({"title": title, "content": text[:1000]})
        print(f"✅ 수집 완료: {title[:30]}...")

# 🧠 4. 분석용 텍스트 가공 (구분자 추가)
combined_text = ""
for i, item in enumerate(articles_data, 1):
    combined_text += f"--- 기사 {i} ---\n제목: {item['title']}\n본문: {item['content']}\n\n"

# 📝 5. 기깔나는 프롬프트 설정
prompt = f"""
당신은 방대한 뉴스를 분석하여 핵심 인사이트를 도출하는 'AI 전략 컨설턴트'입니다.
제공된 15개의 뉴스 데이터를 바탕으로, 사용자가 오늘 반드시 알아야 할 '맥락'을 분석하여 보고서를 작성하세요.

[분석 지침]
1. 개별 기사를 단순히 나열하지 말고, 비슷한 내용끼리 묶어서 '테마별'로 분석하세요.
2. 텔레그램 전송용이므로 가독성을 위해 이모지와 Markdown(볼드체 등)을 적극 사용하세요.
3. '그래서 우리에게 어떤 영향을 주는가?'에 대한 분석을 반드시 포함하세요.

[출력 형식]
📅 **오늘의 뉴스 인사이트 ({', '.join(KEYWORDS)})**

🔍 **1. 한 줄 요약 (Summary)**
- 15개 뉴스를 관통하는 핵심 흐름을 한 문장으로 정리

🗞️ **2. 테마별 주요 이슈 (Core Themes)**
(유사 기사를 묶어 최대 3개 테마로 요약)
• **[테마 제목 1]**: 관련 내용 핵심 요약 및 현재 상황
• **[테마 제목 2]**: 관련 내용 핵심 요약 및 현재 상황

💡 **3. 시사점 및 전망 (Insight)**
- 이 뉴스들이 시장이나 사회에 미칠 영향
- 앞으로 우리가 주의 깊게 살펴봐야 할 포인트

⚠️ **4. 기타 단신**
- 위 테마에 포함되지 않았지만 중요한 개별 소식 1~2개

---
[분석할 뉴스 데이터]:
{combined_text}
"""

# 🤖 6. Gemini 분석 요청
if not articles_data:
    final_message = "❌ 분석할 최신 뉴스를 찾지 못했습니다."
else:
    try:
        print("--- Gemini 분석 중... ---")
        response = model.generate_content(prompt)
        final_message = response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        final_message = "❌ Gemini 요약 도중 오류가 발생했습니다."

# 📲 7. 텔레그램 전송 (Markdown 파싱 적용)
try:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": final_message,
        "parse_mode": "Markdown"
    }
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print("✅ 텔레그램 전송 완료!")
    else:
        print(f"❌ 전송 실패: {res.text}")
except Exception as e:
    print(f"Telegram Error: {e}")
