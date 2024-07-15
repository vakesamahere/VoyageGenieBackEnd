import os
from dotenv import  load_dotenv

load_dotenv()
api_key=os.getenv('API_KEY_QWEN')

base_url = 'https://qwen.ainet.eu.org/v1'

model_name="qwen-max"

#'''
from openai import OpenAI
import json
client = OpenAI(api_key=api_key,base_url=base_url)

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    print("【调用Tool】天气tool被调用了")
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
    #stream=True,
    tools=tool_set1,
    tool_choice="auto"
)
print(stream)
input()
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
#'''