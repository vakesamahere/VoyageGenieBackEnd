import time, sys, json

from crewai import Crew, Process
from agents import RedditAgents
from tasks import RedditTasks

from Tools.search_reddit import RedditSearch
from Tools.get_route import GetRoute

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

# 打字机效果
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

# Ollama API
# llm = Ollama(
#     # model="llama3:70b-instruct-q4_K_M",
#     # model="command-r:plus-Q4_K_M",
#     # model="dbrx:132b-instruct-q4_0",
#     model="deepseek-v2:16b-lite-chat-q4_K_M",
#     base_url="http://192.168.1.18:11434",
#     verbose=True,
#     temperature=0,
#     top_p=0.9,
#     num_predict=-1,
#     # mirostat=2,
#     num_ctx=24576,
# )

# from langchain_anthropic import ChatAnthropic
# llm = ChatAnthropic(
#     model="claude-3-5-sonnet", 
#     verbose=True, 
#     temperature = 0,
#     top_p=0.9,
#     max_tokens=4096,
#     streaming=True,
#     callbacks=[TypewriterStreamHandler(delay=0.02)]
# )

# base_url = "http://localhost:11434/v1/"
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="deepseek-chat", 
    verbose=True, 
    temperature = 0,
    streaming=True,
    max_tokens=4096,
    callbacks=[TypewriterStreamHandler(delay=0.02)]
    )

call_number = 0
agent_finishes = []

# def print_agent_output(agent_output: Union[str, List[Tuple[Dict, str]], AgentFinish], agent_name: str = 'Generic call'):
#     global call_number
#     call_number += 1
#     with open("crew_callback_logs.txt", "a") as log_file:
#         print(f"-{call_number}----Agent Output------------------------------------------", file=log_file)
#         print(f"Agent Name: {agent_name}", file=log_file)
        
#         if isinstance(agent_output, str):
#             try:
#                 agent_output = json.loads(agent_output)
#             except json.JSONDecodeError:
#                 pass
        
#         if isinstance(agent_output, list) and all(isinstance(item, tuple) for item in agent_output):
#             for action, description in agent_output:
#                 print(f"Tool used: {getattr(action, 'tool', 'Unknown')}", file=log_file)
#                 print(f"Tool input: {getattr(action, 'tool_input', 'Unknown')}", file=log_file)
#                 print(f"Action log: {getattr(action, 'log', 'Unknown')}", file=log_file)
#                 print(f"Description: {description}", file=log_file)
#         elif isinstance(agent_output, AgentFinish):
#             agent_finishes.append(agent_output)
#             output = agent_output.return_values
#             print(f"AgentFinish Output: {output['output']}", file=log_file)
#         else:
#             print(f"Unknown format of agent_output:", file=log_file)
#             print(type(agent_output), file=log_file)
#             print(agent_output, file=log_file)
        
#         print("--------------------------------------------------", file=log_file)


agents = RedditAgents()
tasks = RedditTasks()

get_route=GetRoute()

route_planner = agents.routePlanner(llm,tools=[get_route])
# translate_agent = agents.translator()

"""
Rules for defining Reddit search input parameters:
    query: str = Field(
        description="should be query string that post title should contain, or '*' if anything is allowed."
    )
    sort: str = Field(
        description='should be sort method, which is one of: "relevance", "hot", "top", "new", or "comments".'
    )
    time_filter: str = Field(
        description='should be time period to filter by, which is one of "all", "day", "hour", "month", "week", or "year"'
    )
    subreddit: str = Field(
        description='should be name of subreddit, like "all" for r/all'
    )
    limit: str = Field(
        description="a positive integer indicating the maximum number of results to return"
    )
"""
# Initialize Reddit search input parameters.
events=['上海大学','同济大学','复旦']

get_route_task = tasks.get_route(
    agent=route_planner,
    events=events
)
# translate_report = tasks.translate_report(
#     agent=translate_agent,
#     # context=[research_report],
# )

# Create a new Crew instance
crew = Crew(
    agents=[route_planner,
            # translate_agent
            ],
    tasks=[get_route_task,
            # translate_report
            ],
    process=Process.sequential,
    # process=Process.hierarchical,
    # manager_llm=llm,
    # step_callback=lambda x: print_agent_output(x,"Reddit Agent")
)

# Kick of the crew
results = crew.kickoff()

print("Crew usage", crew.usage_metrics)

print("Crew work results:")
print(results)
