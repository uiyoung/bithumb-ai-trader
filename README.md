# bithumb-ai-trader
auto trade bitcoin using AI and bithumb api

## set .env
```bash
BITHUMB_ACCESS_KEY=""
BITHUMB_SECRET_KEY=""
OPENAI_API_KEY=""
SERPAPI_API_KEY=""
TELEGRAM_BOT_TOKEN=""
```

## Install libraries
```bash
pip install -r requirements.txt
```

## AWS EC2 commands
```bash
#한국 기준으로 서버 시간 설정
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

#패키지 목록 업데이트
sudo apt update

#패키지 목록 업그레이드
sudo apt upgrade

#pip3 설치
sudo apt install python3-pip

#가상 환경 만들기 설치
sudo apt install python3.12-venv

#pip3 가상 환경 만들기
python3 -m venv bitcoinenv

#가상 환경 활성화
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

## telegram bot
1. Telegram 앱에서 @BotFather를 검색해서 시작
2. /newbot 명령어 입력
3. 봇 이름과 사용자명 설정
4. BotFather가 API 토큰을 줍니다 (예: 123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)
5. .env에 API 토큰 추가