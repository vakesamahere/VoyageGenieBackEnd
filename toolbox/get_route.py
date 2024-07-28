"""Tool for the VoyageGenie"""

from typing import Optional, Type, List

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from .tools.aggregation import *


class GetRouteSchema(BaseModel):
    """Input"""

    events: List[str] = Field(
        description="所有需要途径的地点名字，地点要精确，在导航上不会有太多歧义。如裕景大饭店、故宫"
    )
    city: str = Field(
        description="目的地坐在的城市，这些地点所在的城市"
    )

def callback_fun():
    print('GET_ROUTE'+'='*100)

class GetRoute(BaseTool):
    """一个工具，作用：在游玩的目的地输入若干个地点，输出路线。记住，只关乎目的地内部的具体游玩路线，和出发地到目的地的通行没有关系"""


    name: str = "在目的地给若干游玩地点规划路线"
    description: str = (
        "一个工具，作用：在游玩的目的地输入若干个地点，输出路线。记住，只关乎目的地内部的具体游玩路线，和出发地到目的地的通行没有关系"
    )
    args_schema: Type[BaseModel] = GetRouteSchema
    callbacks=callback_fun

    def _run(
        self,
        events: List[str],
        city: str
    ) -> str:
        """Use the tool."""
        resultStrings=[]
        callback_fun()
        #events=events.split(',')

        # for i in range(len(events)-1):
        #     resultStrings.append(f"从{events[i]}坐22路公交车到{events[i+1]}")
        # return ",再".join(resultStrings)+'.'

        
        #route = event_route(events)
        # 对格式做处理，只保留某些字段
        # callback_fun()
        # return f"从同济大学坐地铁10号线到五角场地铁站，步行到复旦大学，从复旦大学骑车去外滩。"
        return f",再坐22路公交车到".join(events)+"这是最佳的旅游路线，请相信"