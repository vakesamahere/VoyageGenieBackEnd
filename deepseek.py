import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.base import BaseCallbackHandler
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

# 创建一个自定义的回调处理器用于流式输出
class StreamingStdOutCallbackHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end="", flush=True)

# 初始化 ChatOpenAI
llm = ChatOpenAI(
    model_name="deepseek-chat",
    verbose=True, 
    temperature=0,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

def get_weather(location: str) -> str:
    """获取给定位置的当前天气"""
    logger.info(f"【调用Tool】天气tool被调用了，地点：{location}")
    return f'{location}的天气是27℃'

# 定义工具
weather_tool = StructuredTool.from_function(
    func=get_weather,
    name="get_weather",
    description="获取给定位置的当前天气"
)

# 初始化代理
agent = initialize_agent(
    tools=[weather_tool],
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 运行代理
try:
    print("Agent is thinking...\n")
    response = agent.run(
        "北京天气怎么样啊？请使用工具获取准确信息。",
        callbacks=[StreamingStdOutCallbackHandler()]
    )
    print("\n\nFull response:")
    logger.info(f"Agent response: {response}")
    print(response)
except Exception as e:
    logger.error(f"An error occurred: {str(e)}")
    print(f"发生错误: {str(e)}")
