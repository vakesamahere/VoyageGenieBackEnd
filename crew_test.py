from uuid import UUID
from crewai import Crew, Agent, Task, Process
from langchain_core.outputs import LLMResult
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_anthropic import ChatAnthropic

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain.callbacks.base import BaseCallbackHandler

from dotenv import load_dotenv
load_dotenv()

# 创建一个自定义的回调处理器用于流式输出
class StreamingStdOutCallbackHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end="", flush=True)
    def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
         print(f"ON_LLM_END:{str(response.llm_output)}")
         return super().on_llm_end(response, run_id=run_id, parent_run_id=parent_run_id, **kwargs)

class Location(BaseModel):
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")

class Point(BaseModel):
    name: str = Field(..., description="地点名称")
    address: str = Field(..., description="地点的地址")
    location: Location = Field(..., description="地点的经纬度")

class Navigation(BaseModel):
    start: Point = Field(..., description="本路线段的起点")
    end: Point = Field(..., description="本路线端的终点")
    transportation: str = Field(..., description="交通方式")
    distance: str = Field(..., description="距离")
    price: str = Field(..., description="花费")

class Event(BaseModel):
    name: str = Field(..., description="地点名称")
    position: str = Field(..., description="地点的经纬度")
    description: str = Field(..., description="地点的描述")
    images: List[str] = Field(..., description="景点图片url的集合")

class Route(BaseModel):
    name: str = Field(..., description="路线名")
    navigation: List[Navigation] = Field(..., description="导航信息")
    events: List[Event] = Field(..., description="路过的景点")

class Jpost(BaseModel):
	"""Market strategy model"""
	title: str = Field(..., description="攻略的标题")
	cover: str = Field(..., description="旅游帖子封面的url")
	images: List[str] = Field(..., description="旅游的图片url集合")
	routes: List[Route] = Field(..., description="旅游每一天的路线")

print('LLM loading')
# llm = ChatAnthropic(
#     model="claude-3-5-sonnet@20240620", 
#     verbose=True, 
#     temperature = 0,
#     top_p=0.9,
#     max_tokens=4096,
#     streaming=True
# )
llm=ChatOpenAI(
     model='gpt-4',
     verbose=True,
     callbacks=[StreamingStdOutCallbackHandler()]
)
print(f'LLM loaded: {llm}')

print("loading agent")
memory = ConversationBufferMemory()

agent = Agent(
    role="person",
    goal="""calculate""",
    backstory="I am a man",
    llm=llm
)
print(f"agent loaded: {agent}")


print("loading task")
task = Task(
    description="""生成一个在上海的旅游帖子""",
    agent=agent,
    expected_output="""JSON format with keys: {format}""",
    llm=llm,
    output_json=Jpost
)
print(f"task loaded: {task}")

print('loading crew')
crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=True
)
print(f"crew loaded: {crew}")



format_json = """
{
  title: string;
  cover: string;
  images: string[];
  text: string;
  routes: {
    name: string;
    navigation: {
      起点: {
        name: string,
        address: string,
        location: {
          latitude: number,
          longitude: number
        }
      },
      终点: {
        name: string,
        address: string,
        location: {
          latitude: number,
          longitude: number
        }
    },
    交通方式: string,
      路程: string,
      价格: string
  }[];
    events: { 
      name: string;
      position: string;
      description: string;
      images: string[];
    }[];
  }[];
}
"""
crew.kickoff(inputs={
    "format":format_json    # expect:9,0
})