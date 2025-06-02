import os
from dotenv import load_dotenv
import python_bithumb
import time
import schedule

# .env 파일에서 API 키 로드
load_dotenv()


# 빗썸 API 연결
access = os.getenv("BITHUMB_ACCESS_KEY")
secret = os.getenv("BITHUMB_SECRET_KEY")
bithumb = python_bithumb.Bithumb(access, secret)

# 현재 잔고 확인
my_krw = bithumb.get_balance("KRW")
my_btc = bithumb.get_balance("BTC")
current_price = python_bithumb.get_current_price("KRW-BTC")

amount = 5000


def buy_now():
  print(f"### Buy Order: {amount:,.0f} KRW ###")
  try:
    bithumb.buy_market_order("KRW-BTC", amount)
  except Exception as e:
    print(f"### Buy Failed: {str(e)} ###")


def run_scheduler():
  print("비트코인 자동 트레이딩 시스템 시작...")
  print("스케줄링된 실행 시간: 매일 03:00")

  # 매일 특정 시간에 작업 실행하도록 스케줄링
  schedule.every().day.at("03:17").do(buy_now)

  # 스케줄 루프 실행
  while True:
    schedule.run_pending()
    time.sleep(60)  # 1분마다 스케줄 확인


# 실행
if __name__ == "__main__":
  run_scheduler()
