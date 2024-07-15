import os
from dotenv import load_dotenv
import logging
from openai import OpenAI
import json

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
api_key = os.getenv('API_KEY_DEEPSEEK')

base_url = 'https://api.deepseek.com/v1'

model_name = "deepseek-chat"

# 创建OpenAI客户端实例
client = OpenAI(api_key=api_key, base_url=base_url)

# 定义一个工具函数
def get_weather(location):
    """Get the current weather in a given location"""
    logging.info("天气tool被调用了，查询地点：%s", location)
    return '27℃'

# 工具集定义
tool_set1 = [
    {
        "type":"function",
        "function":{
            "name": "get_weather",
            "description": "Determine weather in my location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state e.g. 北京, tokyo"
                    }
                },
                "required": [
                    "location"
                ]
            }
        }
    }
]

# 尝试获取流式响应
try:
    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": "北京天气怎么样，调用工具查询"}],
        stream=False,
        tools=tool_set1,
        tool_choice={"type":"function","function":{"name":"get_weather"}}
    )
    chunks = []
    for chunk in stream:
        chunks.append(chunk.choices[0].delta)
        print(chunk.choices[0].delta.content or "", end="")
except Exception as e:
    logging.error("请求流式响应时发生错误：%s", e)
    print(stream)

#http
