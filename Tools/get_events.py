"""Tool for the VoyageGenie"""

from typing import Optional, Type, List, Any, Dict

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from tools.aggregation import *

class GetEventsSchema(BaseModel):
    """Input"""

    city: str = Field(
        description="游玩目的地城市"
    )

    _min: int = Field(
        description="要求返回的最小数量"
    )

    _max: int = Field(
        description="要求返回的最大数量"
    )

class GetEvents(BaseTool):
    """工具"""

    name: str = "在目的地寻找值得一去的地方"
    description: str = (
        "一个工具，作用：输入游玩目的地（城市），输出一系列值得游客一去并且符合用户喜好的旅游地点，包括三类：游玩地点、餐厅、住所。"
    )
    args_schema: Type[BaseModel] = GetEventsSchema

    def _run(
        self,
        city: str,
        _min: int,
        _max: int
    ) -> List[Dict[str,Any]]:
        """Use the tool."""
        foods:Dict[str,Any]=food_data(city,_min,_max)
        sights:Dict[str,Any]=sight_data(city,_min,_max)
        # hotel:dict[str,Any]=hotel_data(city,_min,_max)
        hotels={"count":1,"data":[{"address":"同济大学","city":"上海"}]}
        return [foods,sights,hotels]