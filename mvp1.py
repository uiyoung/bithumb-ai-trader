from openai import OpenAI
import python_bithumb
import os
from dotenv import load_dotenv
load_dotenv()

# 1. 빗썸 차트 데이터 가져오기 (30일 일봉)
df = python_bithumb.get_ohlcv("KRW-BTC", interval="day", count=30)

# 2. AI에게 데이터 제공하고 판단 받기
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are an expert in Bitcoin investing. Tell me whether to buy, sell, or hold at the moment based on the chart data provided. response in json format.\n\nResponse Example:\n{\"decision\": \"buy\", \"reason\": \"some technical reason\"}\n{\"decision\": \"sell\", \"reason\": \"some technical reason\"}\n{\"decision\": \"hold\", \"reason\": \"some technical reason\"}"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": df.to_json()
                }
            ]
        }
    ],
    response_format={
        "type": "json_object"
    }
)
print(response.choices[0].message.content)
