"""Tool for the VoyageGenie"""

from typing import Optional, Type, List

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from .tools.aggregation import *

class GetEventDescriptionSchema(BaseModel):
    """Input"""

    city: str = Field(
        description="目的地城市"
    )
    event: str = Field(
        description="具体的需要被介绍的地点"
    )

def callback_fun():
    print('GET_EVENT_DESCRIPTION'+'='*100)

class GetEventDescription(BaseTool):
    """工具"""


    name: str = "对指定游玩地点做介绍"
    description: str = (
        "一个工具，作用：输入游玩目的地中的一个具体地点，输出有关这个地点的详细信息。"
    )
    args_schema: Type[BaseModel] = GetEventDescriptionSchema
    callbacks=callback_fun

    def _run(
        self,
        city: str,
        event: str
    ) -> str:
        """Use the tool."""
        callback_fun()
        return '同济大学和复旦大学都是中国的顶尖高校，学术氛围浓厚，培养出了多位国之栋梁，科研成果丰富。同时校园环境景色优美，适合任何时候前往游玩。外滩是上海的著名景点，是旅客不容错过的景点，可以看到黄浦江的美丽景色，与陆家嘴金融圈隔江相望，在夜晚颇为震撼。'