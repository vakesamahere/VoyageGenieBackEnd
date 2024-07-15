# Set your OpenAI API key and custom base URL
api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzc29faWQiOiI2Yzg1MzU3My03ZWZlLTQ4NWQtYTQzZS03MjU1ZDJlY2E4MjAiLCJlbWFpbCI6IiIsIm1vYmlsZV9udW1iZXIiOiIxODU1ODcwMTE4MSIsImFyZWFfY29kZSI6Iis4NiIsIm1vYmlsZSI6IjE4NTU4NzAxMTgxIiwiZXhwIjoxNzIxNTA2NDU2LCJhdWQiOiI2NTI4YWQzOTZmYWExMzY3ZmVlNmQxNmMifQ._LFmLrSSznCzLlMRB8omUGr7vPwzSo6EdlsuWAktwHU'
api_key = 'sk-YYzxM47N2GNDoj3nTzOLgwZifyt35cBPWT8zhMkdw6vW2Su5'
base_url = 'https://deepseek.ainet.eu.org/v1/'
base_url = 'https://api.moonshot.cn/v1'
model_name="deepseek-chat"
model_name="moonshot-v1-8k"

#'''
from openai import OpenAI
import json
client = OpenAI(api_key=api_key,base_url=base_url)

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    print("***天气tool被调用了")
    return json.dumps({"location": location, "temperature": "-50", "unit": "°C"})

tool_set1    = [{
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["°C"]},
                    },
                    "required": ["location"],
                },
            },
        }]

stream = client.chat.completions.create(
    model=model_name,
    messages=[{"role": "user", "content": "北京天气怎么样啊"}],
    stream=True,
    tools=tool_set1,
    tool_choice="required"
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
#'''