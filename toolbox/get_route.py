"""Tool for the VoyageGenie"""
import json
from typing import Optional, Type, List, Dict, Any

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from .tools.aggregation import *


class GetRouteSchema(BaseModel):
    """Input"""

    events: List[Dict[str,Any]] = Field(
        description="""所有需要途径的经纬度(location)、地址(字段address)、和城市代码(citycode)，地址在导航上不会有太多歧义。如[{'location': '113.978615,22.537872', 'citycode': '0755', 'address':'...'},...]"""
    )
    # city: str = Field(
    #     description="目的地坐在的城市，这些地点所在的城市"
    # )

def callback_fun(r,content):
    r.event_cache_load(f"[get_route]{json.dumps(content)}")

class GetRoute(BaseTool):
    """一个工具，作用：在游玩的目的地输入若干个地点，输出路线。记住，只关乎目的地内部的具体游玩路线，和出发地到目的地的通行没有关系"""


    name: str = "在目的地给若干游玩地点规划路线"
    description: str = (
        "一个工具，作用：在游玩的目的地输入若干个地点，输出路线。记住，只关乎目的地内部的具体游玩路线，和出发地到目的地的通行没有关系"
    )
    args_schema: Type[BaseModel] = GetRouteSchema
    # callbacks=callback_fun

    # def __init__(self,r):
    #     self.receiver = r

    def _run(
        self,
        events: List[Dict[str,Any]],
        # city: str
    ) -> Dict[str,List]:
        """Use the tool."""
        # resultStrings=[]
        # callback_fun()
        #events=events.split(',')

        # for i in range(len(events)-1):
        #     resultStrings.append(f"从{events[i]}坐22路公交车到{events[i+1]}")
        # return ",再".join(resultStrings)+'.'

        # input_list=[{"address":item.get('address',""),"city":city} for item in events if item.get('address',"")!=""]
        # route = event_route(input_list)
        # route = event_route_start_with_loc(input_list)
        route = event_route_start_with_loc(events)
        # callback_fun(self.receiver,route)
        return route

        # test
        return f",再坐22路公交车到".join(events)+"这是最佳的旅游路线，请相信"