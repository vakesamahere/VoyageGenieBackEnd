# from functools import partial
from crewai import Task
from textwrap import dedent
from datetime import datetime


class RedditTasks():

    today_date = datetime.now().strftime('%Y-%m-%d-%H-%M')

    def search_reddit(self, agent, query, sort, time_filter, subreddit, limit):
        return Task(
            description=dedent(f"""
                Pass the complete Reddit search parameters (subreddit:{subreddit}, query: {query}, sort: {sort}, time_filter: {time_filter}, limit: {limit}) to the agent.
                Search topic data from Reddit subreddit, 
                summarize the information of each topic, and generate reports respectively.
                Note: It must be a complete report, the number of topics should be consistent with the {limit} quantity.
                """),
            agent=agent,
            output_file=f"output/{self.today_date}_Reddit_Report.md",
            expected_output = dedent(f"""
                It's a complete report.
                And must be in Chinese,
                and saved to the specified file. 
                Please use Markdown format, as shown in the following example:                   
                '## 1.post title (标题):
                    - Link to this post: 
                    - Post type (类型):
                    - Highlights (亮点):
                    - Tools and links cited in the post:
                    - Summarize (摘要):
                ... ... '
                """),            
        )

    def translate_report(self, agent):
        return Task(
            description=dedent(f"""Professional translation of the report into Chinese. 
                """),
            agent=agent,
            # context=context,
            output_file=f"output/{self.today_date}_Reddit_Report_ZH.md",
            expected_output = dedent(f"""  
            For your final Outputs use the markdown format.
            Note: that terms such as post title, tool name, function name, model name, company name, etc. retain their original names and do not translate. Keep the format of the original English report.
                """),
        )

    #普通聊天，记忆
    def talk_with_user(self,agent):
        return Task(
            description=dedent(f"""根据用户发送的内容给出陪聊的回复，询问用户信息，与用户沟通兴趣爱好，询问用户旅游的需求 
                """),
            agent=agent,
            expected_output = dedent(f"""  
            回复正常的文字就好
                """),
        )
    
    #往返路线
    def get_route_go_back(self,agent,start,end,planGo,planBack):
        return Task(
            description=dedent(f"""根据用户旅游的出发点和目的地，输出用户出发的地点和用户想要去旅游的地点之间的往返出行方案。
    只关注往返路线，不涉及目的地的具体游玩内容。 
                """),
            agent=agent,
            expected_output = dedent(f"""  
            你的最终答案是文字，最好是中文，出行方案要包括交通工具和始末的站点。严格按照如下格式：
            从{start}去{end}，出行方案：{planGo}
            从{end}回到{start}，出行方案：{planBack}
                """),
        )
    
    #获得景点清单
    def get_events(self,agent):
        return Task(
            description=dedent(f"""为用户寻找目的地城市的游玩地点清单，包括游玩地点、餐厅、住所。你最好使用专业的工具在平台完成搜索 
                """),
            agent=agent,
            expected_output = dedent(f"""  
            你的最终答案是文字，最好是中文，分游玩地点、餐厅、住所三类，把清单呈现给用户。
                """),
        )
    
    #规划路线
    def get_route(self,agent,events):
        return Task(
            description=dedent(f"""为用户在目的地城市的众多游玩地点:{events}规划一条合理的游玩路线。路线包括途径地点的顺序，以及相邻地点之间的出行方案。
                """),
            agent=agent,
            expected_output = dedent(f"""  
            你的最终答案是文字，最好是中文。按照路径一个个讲述两个地点之间的出行方式。出行方式要包括交通交通和始末的站点。
                """),
        )
    
    #介绍景点
    def get_event_description(self,agent):
        return Task(
            description=dedent(f"""为用户要求的游玩地点做简短的介绍。
                """),
            agent=agent,
            expected_output = dedent(f"""  
            你的最终答案是文字，最好是中文。要说出游玩地点的特色。
                """),
        )