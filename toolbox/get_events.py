"""Tool for the VoyageGenie"""

from typing import Optional, Type, List, Any, Dict

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from .tools.aggregation import *

class GetEventsSchema(BaseModel):
    """Input"""

    city: str = Field(
        description="游玩目的地城市"
    )

def callback_fun():
    print('GET_EVENTS'+'='*100)

class GetEvents(BaseTool):
    """工具"""

    name: str = "在目的地寻找值得一去的地方"
    description: str = (
        "一个工具，作用：输入游玩目的地（城市），输出一系列值得游客一去并且符合用户喜好的旅游地点，包括三类：游玩地点、美食、住所。同时包括每个项目的介绍。"
    )
    args_schema: Type[BaseModel] = GetEventsSchema
    callbacks=callback_fun

    def _run(
        self,
        city: str,
    ) -> Dict[str,List[Any]]:
        """Use the tool."""
        # callback_fun()
        # return ['同济大学','复旦大学','外滩','和平饭店(酒店)','味千拉面','五角场商圈','朱家角古镇','南京路商业街','人民广场','虹口足球场']
        # foods:Dict[str,Any]=food_data(city,_min,_max)
        # sights:Dict[str,Any]=sight_data(city,_min,_max)
        # hotel:dict[str,Any]=hotel_data(city,_min,_max)
        
        return entertainment_data(city)