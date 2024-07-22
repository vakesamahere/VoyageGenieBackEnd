from crewai import Agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI

from langchain_community.llms import Ollama

# Human Tools
# human_tools = load_tools(["human"])

class RedditAgents():
    # def __init__(self):
        # self.OpenAIGPT35 = ChatOpenAI(
        #     model_name="gpt-3.5-turbo", temperature=0.7)
        # self.OpenAIGPT4 = ChatOpenAI(model_name="gpt-4", temperature=0.7)
        
        # self.mixtral = Ollama(
        #         # model="nous-hermes2-mixtral:8x7b-dpo-q5_K_M",
        #         model="starling-lm:7b-alpha-q6_K",
        #         base_url="http://localhost:11434",
        #         verbose=True,
        #         temperature=0,
        #         top_p=0.9,
        #         num_predict=-1,
        #         mirostat=2,             
        #         num_ctx=8192,
        #     )
        
        # self.llm = Ollama(
        #     # model="llama3:70b-instruct-q4_K_M",
        #     # model="command-r:plus-Q4_K_M",
        #     # model="dbrx:132b-instruct-q4_0",
        #     model="WizardLM2:8x22B-Q4_K_M",
        #     base_url="http://localhost:11434",
        #     verbose=True,
        #     temperature=0,
        #     top_p=0.9,
        #     num_predict=-1,
        #     mirostat=2,
        #     num_ctx=52000,
        # )

        # openai_api_key = 'taSncDAGzfe97eCUtEbeRUpGuAAWnypi0VE6y6JDj4ivqALV'
        # # base_url = os.environ.get("OPENAI_API_BASE")
        # # openai_api_key = os.environ.get("DEEPSEEK_API_KEY")
        # base_url = 'http://localhost:8080/v1'
        # self.llm = ChatOpenAI(model='accounts/fireworks/models/nous-hermes-2-mixtral-8x7b-dpo-fp8', verbose=True, temperature = 0, openai_api_key=openai_api_key, base_url=base_url) # Loading GPT-3.5
    
    def reddit_researcher(self, llm, search_tool):
        return Agent(
            role = "Senior Researcher",
            goal=f"Find and explore the most exciting information on Reddit",
            backstory="""You are an information expert and know how to discover exciting information.
            You're great at finding interesting, exciting projects on any subreddit. You transform the scraped data into reports with specific content. Only data scraped from Reddit subreddits is used in the report.
            """,
            verbose=True,
            allow_delegation=False,
            tools=[search_tool],
            max_iter=10,
            llm=llm,
            # function_calling_llm=llm,
        )

    def translator(self, llm):
        return Agent(
            role="translator",
            goal="Translate text into the language of the specified country",
            backstory="""As a professional translator, you are familiar with the languages ​​of various countries, and are especially able to translate with warmth and sensitivity based on the characteristics and habits of the target language. """,
            verbose=True,
            llm=llm,
            allow_delegation=False,
            max_iter=10,
            # tools=[search_tool, ContentTools.read_content],
        )

    # 需求分析，聊天
    def talker(self, llm):
        return Agent(
            role="talker",
            goal="和用户畅快聊天，并且询问用户有关旅游的需求",
            backstory="""作为一个善于交谈的人，你想尽可能帮用户解决旅游相关的问题。但是你没有能力解决，所以你发挥自身优势，引导用户向你透露更多他们的旅游需求和爱好。你想知道他们从哪里出发，想去哪里旅游，喜欢玩什么。由于自身能力的缺乏，得知用户需求之后，你会委托其他人帮你完成任务。 """,
            verbose=True,
            llm=llm,
            allow_delegation=True,
            max_iter=2,
            # tools=[search_tool, ContentTools.read_content],
        )
    
    # 路线规划
    def routePlanner(self, llm, tools=[]):
        return Agent(
            role="planner",
            goal="帮用户解决和路线分析相关的问题，提出足够的路线方案，让用户一目了然如何旅行。",
            backstory="""作为一个对于路线规划颇有研究的人，你想尽可能帮用户解决旅游中关于路线的问题。路线相关的问题有且只有两类。第一，出发地和目的地的往返路线与出行方案；第二，在目的地的具体游玩路线与出行方案。你深信不疑：面对问题要先分成上述两类的其中一类，而且一定要使用工具解决问题。 """,
            verbose=True,
            llm=llm,
            allow_delegation=False,
            max_iter=2,
            tools=tools,
        )
    
    # 景点查找
    def eventFinder(self, llm, tools=[]):
        return Agent(
            role="知道当地有哪些值得一去的地方的人",
            goal="为用户提供有关游玩地区的有趣景点、优质饭店、合适住所。",
            backstory="""你对用户想要去游玩的城市内部特别了解，你深信利用工具能根据用户的兴趣找到适合他们的游玩地点。你乐于推荐三类地方：游玩处、餐厅、住所""",
            verbose=True,
            llm=llm,
            allow_delegation=False,
            max_iter=2,
            tools=tools,
        )
    
    # 景点介绍
    def eventTeller(self, llm, tools=[]):
        return Agent(
            role="知道某个地方具体信息的人",
            goal="为用户提供有关某个地方的详细的和旅游相关的信息。",
            backstory="""你善于利用工具找到任何一个地点的详细信息。为了解决用户的需求，你将旅游有关的信息和用户分享""",
            verbose=True,
            llm=llm,
            allow_delegation=False,
            max_iter=2,
            tools=tools,
        )