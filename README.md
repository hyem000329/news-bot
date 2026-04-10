# 📰 AI 뉴스 브리핑 봇

매일 8시 아침 뉴스들을 자동으로 수집하고  
AI가 핵심만 요약해서 텔레그램으로 보내주는 봇입니다.

---

## 🚀 기능

- 뉴스 자동 수집 (Google News)
- 기사 본문 분석
- AI 요약 (Gemini)
- 텔레그램 전송
- 매일 오전 8시 자동 실행

---

## 🧩 설치 방법

### 1️⃣ 텔레그램 봇 만들기

- BotFather 검색
- /newbot 실행
- 토큰 복사

---

### 2️⃣ 채널 생성 후 봇 추가

- 채널 생성
- 봇을 관리자 추가
- 메시지 보내기 권한 허용

---

### 3️⃣ Gemini API 키 발급

👉 https://aistudio.google.com/app/apikey

---

### 4️⃣ GitHub Secrets 설정

Settings → Secrets → Actions

다음 3개 추가:

```
TELEGRAM_TOKEN=봇토큰
CHAT_ID=채널ID
GEMINI_API_KEY=API키
```

---

## ⏰ 실행 방식

- 매일 오전 8시 자동 실행
- GitHub Actions 사용

---

## ⚙️ 커스터마이징

### 🔍 키워드 변경

```python
KEYWORDS = ["관세"]
```

👉 예시:

```python
KEYWORDS = ["AI", "반도체", "금리"]
```

---

### 🤖 프롬프트 변경

```python
prompt = f"""
...
"""
```

👉 여기 수정하면 요약 스타일 변경 가능

---

## 💡 출력 예시

```
📰 오늘의 뉴스 브리핑

[전체 흐름]
...

[핵심 이슈]
- ...
- ...

[시사점]
...
```

---

## 💰 비용

- Telegram: 무료
- Gemini: 무료 한도 있음 (일반 사용 충분)

---

## 📌 참고

- 하루 1회 실행 기준 거의 무료
- 일정 기간 활동 없으면 GitHub Actions 중지될 수 있음

---

## 🙌 공유

이 repo를 복사해서 누구나 사용할 수 있습니다!
