"""Tool for the VoyageGenie"""

from typing import Optional, Type, List

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from .tools.aggregation.result import event_route


class GetRouteSchema(BaseModel):
    """Input"""

    events: List[str] = Field(
        description="所有需要途径的地点名字，地点要精确，在导航上不会有太多歧义。如裕景大饭店、故宫"
    )
    city: str = Field(
        description="目的地坐在的城市，这些地点所在的城市"
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
        events: List[str],
        city: str
    ) -> str:
        """Use the tool."""
        resultStrings=[]
        #events=events.split(',')

        # for i in range(len(events)-1):
        #     resultStrings.append(f"从{events[i]}坐22路公交车到{events[i+1]}")
        # return ",再".join(resultStrings)+'.'

        
        route = event_route(events)
        # 对格式做处理，只保留某些字段
        return route
if __name__ == "__main__":
    res=event_route(
        events = [
            {
                "city": "北京",
                "address": "北京市延庆区G6京藏高速58号出口",
                "location": "100,100"
            },
            {
                "city": "北京",
                "address": "北京市西城区前海西街17号",
            }
        ]
    )
    print(res)