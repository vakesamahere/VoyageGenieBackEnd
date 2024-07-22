"""Tool for the VoyageGenie"""

from typing import Optional, Type, List, int

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from tools.aggregation import *


class GetRouteSchema(BaseModel):
    """Input"""

    events: List[str] = Field(
        description="所有需要途径的地点组成的字符串,用英文逗号隔开"
    )

class GetRoute(BaseTool):
    """一个工具，作用：在游玩的目的地输入若干个地点，输出路线。记住，只关乎目的地内部的具体游玩路线，和出发地到目的地的通行没有关系"""

    name: str = "在目的地给若干游玩地点规划路线"
    description: str = (
        "一个工具，作用：在游玩的目的地输入若干个地点，输出路线。记住，只关乎目的地内部的具体游玩路线，和出发地到目的地的通行没有关系"
    )
    args_schema: Type[BaseModel] = GetRouteSchema

    def _run(
        self,
        events: List[str]
    ) -> str:
        """Use the tool."""
        resultStrings=[]
        #events=events.split(',')
        # for i in range(len(events)-1):
        #     resultStrings.append(f"从{events[i]}坐22路公交车到{events[i+1]}")
        # return ",再".join(resultStrings)+'.'
        route = event_route(events)
        # 对格式做处理，只保留某些字段
        return 