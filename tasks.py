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
    
    #json报告
    def json_post(self,agent,context=[]):
        return Task(
            description=dedent(f"""为用户撰写一篇旅行攻略的帖子，用json格式。
                """),
            agent=agent,
            context=context,
            output_json="JSON",
            expected_output = dedent(f"""  
            你的最终答案必须用中文回复。
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
                               4.涉及的地点必须来自上下文中Cerium提供的游玩地点清单；涉及的路线信息必须来自上下文中Vake规划的路线，不得作出修改
                """),
            # agent=agent,
            context=context,
            expected_output = dedent(f"""  
            若你要询问信息，生成你的问题即可。
            若你制定旅行计划，则生成像这样格式的完整报告：
            1.标题：本次旅行的标题
            2.描述：本次旅行简介
            3.路线：
                                     严格根据任务上下文得到的路线信息生成，每条路线的名称，点对点的交通方式，让用户真的知道如何出行。示例：
                                            3.1第一天：外滩和浦东

                                            3.1.1. 从外滩开始您的一天（外滩）
                                            - 地址：黄浦区中山东一路
                                            - 花费大约1-2小时探索这个历史悠久的滨水区

                                            3.1.2. 步行前往南京路步行街（南京路步行街）
                                            - 地址：黄浦区南京东路
                                            - 享受购物和当地小吃大约1-2小时

                                            3.1.3. 前往东方明珠塔（东方明珠）
                                            - 地址：浦东新区世纪大道1号
                                            - 乘坐地铁2号线从南京东路到陆家嘴站（大约15分钟）
                                            - 花费2-3小时参观塔楼并欣赏美景

                                            交通提示：使用地铁作为景点间的高效旅行方式。考虑购买上海公共交通卡以方便出行。

                                            3.2第二天：老城区和博物馆

                                            3.2.1. 从豫园开始您的一天（豫园）
                                            - 地址：黄浦区安仁街132号
                                            - 花费大约2小时探索这个古典园林和附近的集市

                                            3.2.2. 步行至上海博物馆（上海博物馆）
                                            - 地址：黄浦区人民大道201号
                                            - 大约30分钟步行或短暂的地铁行程（从豫园乘坐10号线到新天地，然后换乘1号线到人民广场）
                                            - 允许2-3小时参观博物馆

                                            3.2.3. 探索人民广场区域
                                            - 在下午晚些时候和晚上花时间享受周边区域、公园和商店

                                            交通提示：今天的景点相对接近。步行或短途地铁行程是体验城市氛围的理想方式。

                                            3.3第三天：上海迪士尼乐园

                                            3.3.1. 上海迪士尼乐园（上海迪士尼乐园）
                                            - 地址：浦东新区黄赵路310号
                                            - 乘坐地铁11号线从人民广场直接到迪士尼站（大约1小时）
                                            - 在公园度过全天（上午9:00开门，关闭时间不同）
                                            请根据您的具体需求调整上述翻译内容。
            4.地点详解：
                                     根据任务上下文得到的信息，找出每个地点，写出上下文中涉及的介绍信息
                """)
        )