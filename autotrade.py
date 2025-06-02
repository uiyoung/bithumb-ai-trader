import os
import json
import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import python_bithumb
from openai import OpenAI
import time
import schedule
import asyncio
import telegram

# .env 파일에서 API 키 로드
load_dotenv()


ACCESS_KEY = os.getenv("BITHUMB_ACCESS_KEY")
SECRET_KEY = os.getenv("BITHUMB_SECRET_KEY")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


def init_db():
  # SQLite 데이터베이스 초기화 함수
  conn = sqlite3.connect('bitcoin_trading.db')
  c = conn.cursor()
  c.execute('''CREATE TABLE IF NOT EXISTS trades
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  decision TEXT,
                  percentage INTEGER,
                  reason TEXT,
                  btc_balance REAL,
                  krw_balance REAL,
                  btc_price REAL)''')
  conn.commit()
  return conn


def log_trade(conn, decision, percentage, reason, btc_balance, krw_balance, btc_price):
  # 거래 정보를 DB에 기록하는 함수
  c = conn.cursor()
  timestamp = datetime.now().isoformat()
  c.execute("""INSERT INTO trades 
                 (timestamp, decision, percentage, reason, btc_balance, krw_balance, btc_price) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (timestamp, decision, percentage, reason, btc_balance, krw_balance, btc_price))
  conn.commit()


def get_db_connection():
  # DB 연결 가져오기
  return sqlite3.connect('bitcoin_trading.db')


def get_recent_trades(conn, limit=5):
  c = conn.cursor()

  c.execute("""
    SELECT timestamp, decision, percentage, reason, btc_balance, krw_balance, btc_price
    FROM trades
    ORDER BY timestamp DESC
    LIMIT ?
    """, (limit,))

  columns = ['timestamp', 'decision', 'percentage', 'reason', 'btc_balance', 'krw_balance', 'btc_price']
  trades = []

  for row in c.fetchall():
    trade = {columns[i]: row[i] for i in range(len(columns))}
    trades.append(trade)

  conn.close()
  return trades


def get_bitcoin_news(query="bitcoin", location="us", language="en", num_results=5):
  SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
  api_url = "https://serpapi.com/search.json"
  params = {
      "engine": "google_news",
      "q": query,
      "gl": location,
      "hl": language,
      "api_key": SERPAPI_API_KEY
  }

  response = requests.get(api_url, params=params)
  response.raise_for_status()
  results = response.json()

  news_data = []
  if "news_results" in results:
    for news_item in results["news_results"][:num_results]:
      news_data.append({
          "title": news_item.get("title"),
          "date": news_item.get("date")
      })
  return news_data


async def send_telegram_message(text):
  try:
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
  except Exception as e:
    print(f"[TELEGRAM ERROR] {str(e)}")


def get_ai_decision(conn):
  # 차트 데이터 수집
  short_term_df = python_bithumb.get_ohlcv("KRW-BTC", interval="minute60", count=24)
  mid_term_df = python_bithumb.get_ohlcv("KRW-BTC", interval="minute240", count=30)
  long_term_df = python_bithumb.get_ohlcv("KRW-BTC", interval="day", count=30)

  # 뉴스 데이터 수집
  news_articles = get_bitcoin_news("bitcoin", "us", "en", 5)

  # 현재 잔고 확인
  bithumb = python_bithumb.Bithumb(ACCESS_KEY, SECRET_KEY)
  krw_balance = bithumb.get_balance("KRW")
  btc_balance = bithumb.get_balance("BTC")
  current_btc_price = python_bithumb.get_current_price("KRW-BTC")

  # 최근 거래 내역 가져오기
  recent_trades = get_recent_trades(conn, limit=5)

  # 데이터 페이로드 준비
  data_payload = {
      "short_term": json.loads(short_term_df.to_json()) if short_term_df is not None else None,
      "mid_term": json.loads(mid_term_df.to_json()) if mid_term_df is not None else None,
      "long_term": json.loads(long_term_df.to_json()) if long_term_df is not None else None,
      "news": news_articles,
      "current_balance": {
          "krw": krw_balance,
          "btc": btc_balance,
          "btc_price": current_btc_price,
          "total_value": krw_balance + (btc_balance * current_btc_price)
      },
      "recent_trades": recent_trades
  }

  script = """
                You are an expert in Bitcoin investing.

                Analyze the provided data:
                1. Chart Data: Multi-timeframe OHLCV data ('short_term': 1h, 'mid_term': 4h, 'long_term': daily).
                2. News Data: Recent Bitcoin news articles with 'title' and 'date'.
                3. Current Balance: Current KRW and BTC balances and current BTC price.
                4. Recent Trades: History of recent trading decisions and their outcomes.

                When analyzing recent trades:
                - Evaluate if previous decisions were profitable
                - Check if market conditions have changed since the last trade
                - Consider how the market reacted to your previous decisions
                - Learn from successful and unsuccessful trades
                - Maintain consistency in your strategy unless there's a clear reason to change

                **Task:** Based on technical analysis, news sentiment, and trading history, decide whether to **buy**, **sell**, or **hold** Bitcoin.
                For buy or sell decisions, include a percentage (1-100) indicating what portion of available funds to use.

                **Output Format:** Respond ONLY in JSON format like:
                {"decision": "buy", "percentage": 20, "reason": "some technical reason"}
                {"decision": "sell", "percentage": 50, "reason": "some technical reason"}
                {"decision": "hold", "percentage": 0, "reason": "some technical reason"}
                """
  script2 = """
            You are an expert in Bitcoin investing.

            Analyze the provided data:
            1. Chart Data: Multi-timeframe OHLCV data ('short_term': 1h, 'mid_term': 4h, 'long_term': daily).
            2. News Data: Recent Bitcoin news articles with 'title' and 'date'.
            3. Current Balance: Current KRW and BTC balances and current BTC price.
            4. Recent Trades: History of recent trading decisions and their outcomes.

            When analyzing recent trades:
            - Evaluate if previous decisions were profitable
            - Check if market conditions have changed since the last trade
            - Consider how the market reacted to your previous decisions
            - Learn from successful and unsuccessful trades
            - Maintain consistency in your strategy unless there's a clear reason to change

            **Task:** Based on technical analysis, news sentiment, and trading history, decide whether to **buy** or **sell** Bitcoin.
            For buy or sell decisions, include a percentage (1-100) indicating what portion of available funds to use.

            **Output Format:** Respond ONLY in JSON format like:
            {"decision": "buy", "percentage": 20, "reason": "some technical reason"}
            {"decision": "sell", "percentage": 50, "reason": "some technical reason"}
            """

  # OpenAI GPT에게 판단 요청
  client = OpenAI()
  response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
          {
              "role": "system",
              "content": script2
          },
          {
              "role": "user",
              "content": json.dumps(data_payload)
          }
      ],
      response_format={"type": "json_object"}
  )

  # AI 응답 처리
  result = json.loads(response.choices[0].message.content)
  asyncio.run(send_telegram_message(f"### AI Decision: {result['decision'].upper()} ###"))

  return result


def execute_trade():
  # 트레이딩 실행 함수

  # 데이터베이스 초기화
  conn = init_db()

  # 로그에 실행 시간 기록
  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  print(f"[{current_time}] 트레이딩 작업 실행 중...")

  # AI 결정 얻기
  result = get_ai_decision(conn)
  print(result)

  # 빗썸 API 연결
  bithumb = python_bithumb.Bithumb(ACCESS_KEY, SECRET_KEY)

  # 잔고 확인
  # krw_balance = bithumb.get_balance("KRW")
  # btc_balance = bithumb.get_balance("BTC")

  ai_decision = result["decision"]
  reason = result["reason"]
  percentage = result.get("percentage", 0)  # 투자 비율 (0-100%)

  # 최소 금액과 최대 금액 설정
  min_amount = 10100
  max_amount = 20000
  normalized_percentage = percentage / 100.0

  order_executed = False

  # order by ai decision
  if ai_decision == "buy":
    amount = (min_amount + (max_amount - min_amount) * normalized_percentage) / 0.997

    print(f"### Buy Order: {amount:,.0f} KRW ###")

    try:
      bithumb.buy_market_order("KRW-BTC", amount)
      order_executed = True
    except Exception as e:
      print(f"### Buy Failed: {str(e)} ###")

    asyncio.run(send_telegram_message(f"### Buy Order: {amount:,.0f} KRW ###"))
  elif ai_decision == "sell":
    current_btc_price = python_bithumb.get_current_price("KRW-BTC")
    target_value = min_target_value + (max_target_value - min_target_value) * normalized_percentage
    btc_amount = (target_value / current_btc_price) / 0.997

    print(f"### Sell Order: {btc_amount} BTC, amount: {target_value:,.0f} KRW ###")

    try:
      bithumb.sell_market_order("KRW-BTC", btc_amount)
      order_executed = True
    except Exception as e:
      print(f"### Sell Failed: {str(e)} ###")

    asyncio.run(send_telegram_message(f"### Sell Order: {btc_amount} BTC, amount: {target_value:,.0f} KRW ###"))
  elif ai_decision == "hold":
    print("### Hold Position ###")
    order_executed = True  # 'hold'도 성공한 결정으로 간주

  # 잔고 업데이트를 위해 잠시 대기
  time.sleep(1)

  # 거래 후 최신 잔고 조회
  updated_krw = bithumb.get_balance("KRW")
  updated_btc = bithumb.get_balance("BTC")
  updated_price = python_bithumb.get_current_price("KRW-BTC")

  # 거래 정보 로깅
  log_trade(
      conn,
      ai_decision,
      percentage if order_executed else 0,
      reason,
      updated_btc,
      updated_krw,
      updated_price
  )

  conn.close()

  print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 트레이딩 작업 완료")


def run_scheduler():
  print("비트코인 자동 트레이딩 시스템 시작...")

  SCHEDULE_TIME = "03:17"
  print(f"스케줄링된 실행 시간: 매일 {SCHEDULE_TIME}")

  schedule.every().day.at("09:00").do(get_ai_decision)
  schedule.every().day.at(SCHEDULE_TIME).do(execute_trade)
  schedule.every().day.at("11:00").do(get_ai_decision)

  # 매일 특정 시간에 작업 실행하도록 스케줄링
  # print("스케줄링된 실행 시간: 매일 09:00, 15:00, 21:00")
  # schedule.every().day.at("09:00").do(execute_trade)
  # schedule.every().day.at("15:00").do(execute_trade)
  # schedule.every().day.at("21:00").do(execute_trade)

  # 스케줄 루프 실행
  while True:
    schedule.run_pending()
    time.sleep(60)  # 1분마다 스케줄 확인


# 실행
if __name__ == "__main__":
  run_scheduler()
