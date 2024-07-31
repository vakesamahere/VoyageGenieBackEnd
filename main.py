import time, sys, json
from uuid import UUID

from crewai import Crew, Process
from langchain_core.outputs import LLMResult
from agents import RedditAgents
from tasks import RedditTasks

from toolbox.get_route import GetRoute
from toolbox.get_event_description import GetEventDescription
from toolbox.get_events import GetEvents
from toolbox.get_route_go_back import GetRouteGoBack
from toolbox.tools.aggregation import result

from langchain.schema import AgentFinish
from typing import Union, List, Tuple, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
# from file_io import save_markdown
import logging

# 配置logging
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别为DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到控制台
    ]
)

# 获取一个logger实例
logger = logging.getLogger(__name__)
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
    def __init__(self, delay=0.02,receiver=None):
        self.delay = delay
        self.last_output_time = 0
        self.receiver=receiver
    
    def receiver_send(self,string):
        if not self.receiver:
            print('no receiver')
            return
        self.receiver.cache_load(string)

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        current_time = time.time()
        self.receiver_send(token)
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
    
    def on_tool_end(self, output: Any, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        print(output)
        with open('./output/on_tool_end.txt','a',encoding='utf-8') as f:
            f.write(str(output))
        return super().on_tool_end(output, run_id=run_id, parent_run_id=parent_run_id, **kwargs)
 
def run_crew(receiver,msg):
    print('receiver loading')
    print('receiver loaded')

    print('LLM loading')
    # llm = ChatOpenAI(
    #     model="deepseek-chat", 
    #     verbose=True, 
    #     temperature = 0,
    #     streaming=True,
    #     max_tokens=4096,
    #     callbacks=[TypewriterStreamHandler(delay=0.02,receiver=receiver)]
    #     )
    # print(f'base_url: {llm.openai_api_base}')
    llm = ChatAnthropic(
        model="claude-3-5-sonnet@20240620", 
        verbose=True, 
        temperature = 0,
        top_p=0.9,
        max_tokens=4096,
        streaming=True,
        callbacks=[TypewriterStreamHandler(delay=0.02, receiver=receiver)]
    )
    print('LLM loaded')

    print('agents loading')
    agents = RedditAgents()
    print(f'agent loaded')
    print('tasks loading')
    tasks = RedditTasks()
    print(f'tasks loaded')

    def crew():
        print('loading each agent')
        manager = agents.manager(llm)
        print(f'manager loaded')
        event_finder=agents.eventFinder(llm,[GetEvents(
            # receiver
            )])
        print(f'event_finer loaded')
        event_teller=agents.eventTeller(llm,[GetEventDescription()])
        print(f'event_teller loaded')
        route_planner=agents.routePlanner(llm,[GetRoute(
            # receiver
            )])
        print(f'route_planner loaded')
        go_back_planner=agents.gobackPlanner(llm,[GetRouteGoBack(
            # receiver
            )])
        print(f'go_back_planner loaded')
        writer=agents.writer(llm)
        print(f'writer loaded')
        friend=agents.friend(llm)
        print(f'friend loaded')

        print('loading each task')
        # task_talk_with_user = tasks.talk_with_user(agent=talker)
        # print(f'task_talk_with_user loaded')
        task_get_events = tasks.get_events(agent=event_finder,context=[
            #task_talk_with_user
            ])
        print(f'task_get_events loaded')
        task_get_route = tasks.get_route(agent=route_planner,context=[
            task_get_events,
            #task_talk_with_user
            ])
        print(f'task_get_route loaded')
        task_get_route_go_back = tasks.get_route_go_back(agent=go_back_planner,context=[
            #task_talk_with_user
            ])
        print(f'task_get_route_go_back loaded')
        task_get_desc = tasks.get_event_description(agent=event_teller,context=[
            task_get_events,
            #task_talk_with_user
            ])
        print(f'task_get_event_desc loaded')
        task1 = tasks.all(
            agent=writer,
            context=[
                #task_talk_with_user,
                task_get_events,
                task_get_desc,
                task_get_route,
                task_get_route_go_back
                ]
        )
        print(f'task_all loaded')
        # Create a new Crew instance
        print('loading crew')
        crew = Crew(
            agents=[
                #talker,
                event_finder,
                # event_teller,
                route_planner,
                go_back_planner,
                writer,
                ],
            tasks=[
                #task_talk_with_user,
                # task_get_events,
                # task_get_route_go_back,
                # task_get_route,
                # task_get_desc,
                task1,
                ],
            manager_agent=manager,
            process=Process.hierarchical
            # memory=True,
            # embedder={
            #     "provider": "openai",
            #     "config":{
            #         "model": 'text-multilingual-embedding-002'
            #     }
            # }

            # process=Process.hierarchical,
            # manager_llm=llm,
            # step_callback=lambda x: print_agent_output(x,"Reddit Agent")
        )
        print(f'crew loaded\n{crew}')
        return crew
    print('crew kicking off...')
    # Kick of the crew
    # history="user: 明天从北京去上海玩\n"
    # while True:
    #     results = crew().kickoff(inputs={
    #         "city_from":"",
    #         "city_to": "",
    #         "history":history
    #         })
    #     history+=f"AI:{results.raw}\n"
    #     new_input=input("chat with AI: ")
    #     history+=f"user:{new_input}\n"
    #     print(f"history:{history}")
    history=msg
    results = crew().kickoff(inputs={
        "city_from":"",
        "city_to": "",
        "history":history
        })
    print(f'finish')
    print("Crew usage", crew.usage_metrics)

    print("Crew work results:")
    print(results)
    return result

if __name__ == "__main__":
    import server
    run_crew(server.Receiver(),'明天从北京去上海玩')