import os
from uuid import UUID
from dotenv import load_dotenv
from langchain_core.outputs import LLMResult
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseChatMessageHistory
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent, AgentType
from langchain_core.callbacks import BaseCallbackHandler
import logging
load_dotenv()
# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)


class StreamingStdOutCallbackHandler(BaseCallbackHandler):
    def __init__(self,receiver) -> None:
        super().__init__()
        self.receiver=receiver
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end="", flush=True)
        self.receiver.send_stream(token)
    def on_llm_end(self):
        self.receiver.send_end()

class AgentChat:
    def __init__(self,receiver) -> None:
        self.receiver=receiver

        # 初始化 ChatOpenAI
        self.llm = ChatOpenAI(
            base_url="https://api.deepseek.com/v1",
            model_name="deepseek-chat",
            verbose=True, 
            temperature = 0,
            top_p=0.9,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler(self.receiver)]
        )

        # 定义工具
        self.tools=[
            StructuredTool.from_function(
                func=get_weather,
                name="get_weather",
                description="获取给定位置的当前天气"
            )
        ]

        # 初始化代理
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            

        )

    #发送聊天信息
    def chat(self,newText):
        # 运行代理
        try:
            response = self.agent.run(newText)
            logger.info(f"Agent response: {response}")
            print(response)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            print(f"发生错误: {str(e)}")
    
    def loadMsg(self,msgs):
        for msg in msgs:
            role = msg.get('role',False)
            if not role:
                logger.error("Invalid Role")
                return
        #没写完呢
            


#定义工具
def get_weather(location: str) -> str:
    """获取给定位置的当前天气"""
    logger.info(f"【调用Tool】天气tool被调用了，地点：{location}")
    return f'{location}的天气是27℃'
'''
agentChat=AgentChat(Receiver())
agentChat.chat("北京天气如何")
#'''