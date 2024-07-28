# from functools import partial
from crewai import Task
from textwrap import dedent
from datetime import datetime
from toolbox import *
import agents

# 设定context(handle input),callback(handle output),agent,tools

class RedditTasks():

    today_date = datetime.now().strftime('%Y-%m-%d-%H-%M')

    #普通聊天，记忆
    def talk_with_user(self,agent):
        return Task(
            description=dedent(f"""根据用户发送的内容给出陪聊的回复，询问用户信息，与用户沟通兴趣爱好，询问用户旅游的需求，得到用户关于旅游的信息，不用太详细，只要包括出发地、目的地、爱好。
                """),
            agent=agent,
            expected_output = dedent(f"""  
            用户对旅游的需求信息
                """),
        )
    
    #往返路线
    def get_route_go_back(self,agent,context=[]):
        return Task(
            description=dedent("""根据用户旅游的出发点{city_from}和目的地{city_to}，输出用户出发的地点和用户想要去旅游的地点之间的往返出行方案。
    只关注往返路线，不涉及目的地的具体游玩内容。 
                """),
            agent=agent,
            tools=[GetRoute],
            context=context,
            expected_output = dedent(f"""  
            你的最终答案是文字，最好是中文，出行方案要包括交通工具和始末的站点。严格按照如下格式：
                """),
        )
    
    #获得景点清单
    def get_events(self,agent,context=[]):
        return Task(
            description=dedent("""为用户寻找目的地城市{city_to}的游玩地点清单，包括游玩地点、餐厅、住所。你最好使用专业的工具在平台完成搜索 
                """),
            agent=agent,
            tools=[GetEvents],
            context=context,
            expected_output = dedent(f"""  
            你的最终答案是文字，最好是中文，分游玩地点、餐厅、住所三类，把清单呈现给用户。还必须根据搜索的结果，附上每个项目的简介。
                """),
        )
    
    #规划路线
    def get_route(self,agent,context=[]):
        print('creating task get_route')
        return Task(
            description=dedent("""为用户在目的地城市{city_to}的众多游玩地点规划一条合理的游玩路线。路线包括途径地点的顺序，以及相邻地点之间的出行方案。
                """),
            agent=agent,
            tools=[GetRoute],
            context=context,
            expected_output = dedent(f"""  
            你的最终答案是文字，最好是中文。按照路径一个个讲述两个地点之间的出行方式。出行方式要包括交通交通和始末的站点。
                """),
        )
    
    #介绍景点
    def get_event_description(self,agent,context=[]):
        return Task(
            description=dedent(f"""为用户要求的游玩地点做简短的介绍。
                """),
            agent=agent,
            context=context,
            expected_output = dedent(f"""  
            你的最终答案是文字，最好是中文。要说出游玩地点的特色。
                """),
        )
    
    #总任务
    def all(self,agent,context=[]):
        return Task(
            description=dedent("""
                               基于用户与你之前交谈的内容:{history}。判断是否已经收集足够了用户的完整信息（只包括关键的三个信息：目的地、出发地、出发时间。切记：不要别的，别的是你要为用户定制的！）
                               如果你认为关键的三个信息收集还需继续，你就什么也不要做，得出最终答案：请提供更多信息。
                               否则（你认为信息足够），你就可以开始为用户定制旅行计划了，这是你确保信息收集完毕之后的任务：为用户做一个从{city_from}到{city_to}的旅行计划。包含往返方案，目的地游玩地点推荐，目的地游玩路线规划的完整旅行计划。
            在完成任务的过程中：
                               1.你只使用中文
                               2.每个同事最多请一次、最少也请一次
                               3.做好分工，做好委派
                """),
            # agent=agent,
            context=context,
            expected_output = dedent(f"""  
            你的最终答案是完整的安排，最好是中文。事无巨细都要安排好！
                """)
        )