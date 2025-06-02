# bithumb-ai-trader
auto trade bitcoin using AI and bithumb api

## Getting Your API Keys
1. Bithumb API
    - https://www.bithumb.com/react/api-support/management-api
      - 실행시킬 환경의 IP를 허용 IP주소로 추가(API Key 발급 내역 - 허용 IP주소)

2. OpenAI API
    - https://platform.openai.com/api-keys

3. SerpAPI
    - https://serpapi.com/

4. Telegram Bot Token
    - https://t.me/BotFather
      1. /newbot 명령어 입력
      2. 봇 이름과 사용자명 설정
      3. BotFather가 알려주는 API 토큰을 복사하여 .env의 `TELEGRAM_BOT_TOKEN`값으로 추가

5. Telegram Chat Id
    - https://t.me/get_id_bot
      - 위 봇을 실행하고, 텔레그램에서 봇과 대화를 나누면 위 봇이 알려주는 Chat ID를 .env의 `TELEGRAM_CHAT_ID`값으로 추가

## set .env file
```bash
BITHUMB_ACCESS_KEY=
BITHUMB_SECRET_KEY=
OPENAI_API_KEY=
SERPAPI_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## Install libraries
```bash
pip install -r requirements.txt --upgrade
```

## ubuntu commands
```bash
# 한국 기준으로 서버 시간 설정
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

# 패키지 목록 업데이트
sudo apt update

# 패키지 목록 업그레이드
sudo apt upgrade

# pip3 설치
sudo apt install python3-pip

# 가상 환경 만들기 설치
sudo apt install python3.12-venv

# pip3 가상 환경 만들기
python3 -m venv bitcoinenv

# 가상 환경 활성화
source bitcoinenv/bin/activate
```

## Run autotrade.py
```bash
# 실행
python3 autotrade.py

# 백그라운드 실행
nohup python3 -u autotrade.py > output.log 2>&1 &
```

## Run Dashboard
```bash
# 실행
streamlit run streamlit_app.py --server.port 8501

# 백그라운드 실행
nohup python3 -m streamlit run streamlit_app.py --server.port 8501 > streamlit.log 2>&1 &
```

## Exit app
```bash
# PID 확인
ps ax | grep .py

# 종료하기 e.g. kill -9 13586
kill -9 [PID]
```