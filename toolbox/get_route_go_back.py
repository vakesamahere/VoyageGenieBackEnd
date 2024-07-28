"""Tool for the VoyageGenie"""

from typing import Optional, Type, List

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Any,Dict

from .tools.aggregation import *


class GetRouteGoBackSchema(BaseModel):
    """Input"""

    city_from: str = Field(
        description="出发坐在的城市"
    )
    city_to: str = Field(
        description="目的地坐在的城市"
    )

def callback_fun():
    print('GET_ROUTE'+'='*100)

class GetRouteGoBack(BaseTool):
    """一个工具，作用：在游玩的目的地输入若干个地点，输出路线。记住，只关乎目的地内部的具体游玩路线，和出发地到目的地的通行没有关系"""


    name: str = "规划本次旅行的往返方案"
    description: str = (
        "一个工具，作用：输出旅游出发地到目的地的往返路线。记住，只关乎出发地到目的地的通行，和目的地内部的具体游玩路线没有关系"
    )
    args_schema: Type[BaseModel] = GetRouteGoBackSchema
    callbacks=callback_fun

    def _run(
        self,
        city_from:str,
        city_to:str
    ) -> Dict[str,Any]:
        """Use the tool."""
        resultStrings=[]
        callback_fun()
        #events=events.split(',')

        # for i in range(len(events)-1):
        #     resultStrings.append(f"从{events[i]}坐22路公交车到{events[i+1]}")
        # return ",再".join(resultStrings)+'.'
        # 对格式做处理，只保留某些字段
        # callback_fun()
        # return f"从{city_from}坐飞机到{city_to}，从{city_to}坐高铁回到{city_from}"
        return travel_data(city_from,city_to)