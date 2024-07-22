import os, time, sys
from typing import Dict
from uuid import UUID
from dotenv import load_dotenv
from langchain.chains.llm import LLMChain
from langchain_core.outputs import LLMResult
from langchain.memory.summary import ConversationSummaryMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseChatMessageHistory
from langchain.tools import StructuredTool,tool
from langchain.agents import initialize_agent, AgentType, ZeroShotAgent, Tool, AgentExecutor
from langchain_core.callbacks import BaseCallbackHandler
from typing import Annotated,List
from pydantic import BaseModel
import logging
load_dotenv()
# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

class TypewriterStreamHandler(BaseCallbackHandler):
    def __init__(self, delay=0.02):
        self.delay = delay
        self.last_output_time = 0

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        current_time = time.time()
        time_since_last_output = current_time - self.last_output_time

        if time_since_last_output < self.delay:
            time.sleep(self.delay - time_since_last_output)

        if token.strip():  # 如果token不是空白字符
            for char in token:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(self.delay)
        elif '\n' in token:  # 如果是换行符
            sys.stdout.write('\n')
            sys.stdout.flush()
            time.sleep(self.delay * 2)  # 在换行时稍微多等一下
        else:  # 其他空白字符
            sys.stdout.write(token)
            sys.stdout.flush()

        self.last_output_time = time.time()


class StreamingStdOutCallbackHandler(BaseCallbackHandler):
    def __init__(self,receiver) -> None:
        super().__init__()
        self.receiver=receiver
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end="", flush=True)
        self.receiver.send_stream(token)
    def on_llm_end(self):
        self.receiver.send_end()
class AgentMemory(ConversationSummaryMemory):
    def __init__(self,llm):
        SUMMARIZER_TEMPLATE = """请将以下内容逐步概括所提供的对话内容，并将新的概括添加到之前的概括中，形成新的概括。
        EXAMPLE
        Current summary:
        Human询问AI对人工智能的看法。AI认为人工智能是一种积极的力量。
        New lines of conversation:
        Human：为什么你认为人工智能是一种积极的力量？
        AI：因为人工智能将帮助人类发挥他们的潜能。
        New summary:
        Human询问AI对人工智能的看法。AI认为人工智能是一种积极的力量，因为它将帮助人类发挥他们的潜能。
        END OF EXAMPLE
        Current summary:
        {summary}
        New lines of conversation:
        {new_lines}
        New summary:"""
        
        SUMMARY_PROMPT=PromptTemplate(
            input_variables=["summary", "new_lines"], 
            template=SUMMARIZER_TEMPLATE
        )
        super().__init__(llm=llm,prompt=SUMMARY_PROMPT, max_token_limit=256, memory_key="chat_history")

class AgentChat:
        
    def __init__(self,receiver) -> None:
        self.prefix = """你是一个旅行规划师，用中文回答客户关于旅行计划的问题。你的回答需要满足以下要求:
        1. 你的回答必须是中文。
        2. 对于具体的问题，你会把问题分三类，用户信息搜集，往返问题，目的地游玩问题。目的地游玩又分为路线规划问题，具体景点介绍问题。
        3. 你的回答是根据具体问题的，你的思路非常清晰，都是先识别问题类别，再针对问题类型作出回答。
        4. 你可以使用工具:
        """
        self.suffix="""
        {chat_history}
        Human: {input}
        AI:"""
    
        self.receiver=receiver

        # 初始化 ChatOpenAI
        from langchain_anthropic import ChatAnthropic
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet", 
            verbose=True, 
            temperature = 0,
            top_p=0.9,
            max_tokens=4096,
            streaming=True,
            callbacks=[TypewriterStreamHandler(delay=0.02)]
        )

        # 定义工具
        self.tools=[
            get_weather,
            get_route,
            get_events,
            get_route_between_cities,
        ]


        # 初始化代理
        self.llm_chain=LLMChain(llm=self.llm,prompt=ZeroShotAgent.create_prompt(
            tools=self.tools,
            prefix=self.prefix,
            suffix=self.suffix,
            input_variables=['input','chat_history','agent_scratchpad']
        ))
        self.memory=AgentMemory(self.llm)

        self.agent = ZeroShotAgent(
            tools=self.tools,
            llm_chain=self.llm_chain,
            verbose=True
        )
        self.agent_chain=AgentExecutor.from_agent_and_tools(
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            max_iterations=5,
            agent=self.agent
        )

    #发送聊天信息
    def chat(self,newText):
        # 运行代理
        #try:
        response = self.agent_chain.invoke({"input":newText})
        logger.info(f"Agent response: {response}")
        print(response)
        '''
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            print(f"发生错误: {str(e)}")#'''
    
    def loadMsg(self, msgs):
        for msg in msgs:
            role = msg.get('role', False)
            if not role:
                logger.error("Invalid Role")
                return
            if role == 'system':
                self.agent.memory.chat_memory.add_message(SystemMessage(content=msg['content']))
            elif role == 'human':
                self.agent.memory.chat_memory.add_message(HumanMessage(content=msg['content']))
            elif role == 'ai':
                self.agent.memory.chat_memory.add_message(AIMessage(content=msg['content']))
            else:
                logger.error(f"Unknown role: {role}")

#定义工具
@tool
def get_weather(
        location: Annotated[str,"需要获取天气的位置"]
        ) -> str:
    """获取给定位置的当前天气"""
    logger.info(f"【调用Tool】天气tool被调用了，地点：{location}")
    return f'{location}的天气是27℃'

@tool
def get_route(
        events:Annotated[str,"所有需要途径的地点，用英文逗号','隔开"]
        )->str:
    """在游玩的目的地输入若干个地点，输出路线。记住，只关乎目的地内部的具体游玩路线，和出发地到目的地的通行没有关系"""
    events=events.split(',')
    resultStrings=[]
    for i in range(len(events)-1):
        resultStrings.append(f"从{events[i]}坐车到{events[i+1]}")
    return ",再".join(resultStrings)+'.'

@tool
def get_events(
    city:Annotated[str,"需要获取景点、餐厅或住所清单的城市，如上海、北京等。"]
)->List[str]:
    """输入城市名称，输出一个在该城市的游玩地点清单，足够满足用户需求，得到回复可以直接交给用户"""
    return ['北京大学','中山大学']

@tool("查询两个城市间的交通工具，输入2个参数，分别代表出发城市和目的城市")
def get_route_between_cities(start_city: str, des_city: str):
    """
    输出用户出发的地点和用户想要去旅游的地点之间的往返出行方案。
    只关注往返路线，不涉及目的地的具体游玩内容。

    参数:
    start_city (str): 出发地
    des_city (str): 目的地

    返回:
    str: 往返的出行方案
    """
    print(start_city, des_city)
    return '坐飞机去'


#end of tools

class Receiver():
    def send_stream(self,text):
        pass
    def send_end(self):
        pass
#'''
if __name__ == "__main__":
    agentChat=AgentChat(Receiver())
    while 1:
        text=input("Type:")
        if text == "":
            break
        agentChat.chat(text)
        logging.debug(agentChat.memory)

#'''
