import os
from dotenv import load_dotenv
import python_bithumb
import asyncio
import telegram
import time
import schedule

# .env 파일에서 API 키 로드
load_dotenv()

ACCESS_KEY = os.getenv("BITHUMB_ACCESS_KEY")
SECRET_KEY = os.getenv("BITHUMB_SECRET_KEY")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KRW_AMOUNT = 10100
SCHEDULE_TIME = "03:17"

# telegram bot
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telegram.Bot(token=telegram_bot_token)

# BITHUMB 잔고 확인
bithumb = python_bithumb.Bithumb(ACCESS_KEY, SECRET_KEY)
my_krw = bithumb.get_balance("KRW")
my_btc = bithumb.get_balance("BTC")


def buy_now():
  current_btc_price = python_bithumb.get_current_price("KRW-BTC")
  print(f"### Buy Order: {KRW_AMOUNT:,.0f} KRW {current_btc_price:,.0f} BTC ###")
  asyncio.run(send_telegram_message(f"### Buy Order: {KRW_AMOUNT:,.0f} KRW {current_btc_price:,.0f} BTC ###"))

  try:
    bithumb.buy_market_order("KRW-BTC", KRW_AMOUNT)
  except Exception as e:
    message = f"### Transaction Failed: {str(e)} ###"
    print(message)
    asyncio.run(send_telegram_message(message))

def sell_now():
  current_btc_price = python_bithumb.get_current_price("KRW-BTC")
  target_btc_amount = KRW_AMOUNT / current_btc_price
  print(f"### Sell Order: {KRW_AMOUNT:,.0f} KRW {target_btc_amount:,.0f} BTC ###")
  asyncio.run(send_telegram_message(f"### Sell Order: {KRW_AMOUNT:,.0f} KRW {target_btc_amount:,.0f} BTC ###"))

  try:
    bithumb.sell_market_order("KRW-BTC", target_btc_amount)
  except Exception as e:
    message = f"### Transaction Failed: {str(e)} ###"
    print(message)
    asyncio.run(send_telegram_message(message))

async def send_telegram_message(text):
  try:
    await bot.send_message(chat_id=CHAT_ID, text=text)
  except Exception as e:
    print(f"[TELEGRAM ERROR] {str(e)}")


def run_scheduler():
  print("비트코인 자동 트레이딩 시스템 시작...")
  print(f"스케줄링된 실행 시간: 매일 {SCHEDULE_TIME}")

  # 매일 특정 시간에 작업 실행하도록 스케줄링
  schedule.every().day.at(SCHEDULE_TIME).do(buy_now)

  # 스케줄 루프 실행
  while True:
    schedule.run_pending()
    time.sleep(60)  # 1분마다 스케줄 확인


# 실행
if __name__ == "__main__":
  run_scheduler()
