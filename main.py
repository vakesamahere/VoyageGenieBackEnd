import time, sys, json

from crewai import Crew, Process
from agents import RedditAgents
from tasks import RedditTasks

from toolbox.search_reddit import RedditSearch
from toolbox.get_route import GetRoute
from toolbox.get_event_description import GetEventDescription
from toolbox.get_events import GetEvents
from toolbox.tools.aggregation import result

from langchain.schema import AgentFinish
from typing import Union, List, Tuple, Dict
# from file_io import save_markdown

from dotenv import load_dotenv
load_dotenv()

from langchain_community.llms import Ollama
# from langchain_groq import ChatGroq
from langchain.callbacks.base import BaseCallbackHandler

# 创建一个自定义的回调处理器用于流式输出
class StreamingStdOutCallbackHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end="", flush=True)

# 打字机效果回调处理器
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

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="deepseek-chat", 
    verbose=True, 
    temperature = 0,
    streaming=True,
    max_tokens=4096,
    callbacks=[TypewriterStreamHandler(delay=0.02)]
    )

agents = RedditAgents()
tasks = RedditTasks()

get_route=GetRoute()

talker = agents.talker(llm)
event_finder=agents.eventFinder(llm,[GetEvents()]),
event_teller=agents.eventTeller(llm,[GetEventDescription()]),
route_planner=agents.routePlanner(llm,[GetRoute()])
friend=agents.friend(llm)

task1 = tasks.all(
    agent=talker
)

# Create a new Crew instance
crew = Crew(
    agents=[talker,
            agents.eventFinder(llm,[GetEvents()]),
            agents.eventTeller(llm,[GetEventDescription()]),
            route_planner,
            friend,
            ],
    tasks=[task1
            ],
    process=Process.sequential,
    # process=Process.hierarchical,
    # manager_llm=llm,
    # step_callback=lambda x: print_agent_output(x,"Reddit Agent")
)

# Kick of the crew
results = crew.kickoff(inputs={"input":"我要从福州到苏州玩", "task_input": "我要从福州到苏州玩"})

print("Crew usage", crew.usage_metrics)

print("Crew work results:")
print(results)
