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

class GetEventDescription(BaseTool):
    """工具"""

    name: str = "对指定游玩地点做介绍"
    description: str = (
        "一个工具，作用：输入游玩目的地中的一个具体地点，输出有关这个地点的详细信息。"
    )
    args_schema: Type[BaseModel] = GetEventDescriptionSchema

    def _run(
        self,
        city: str,
        event: str
    ) -> str:
        """Use the tool."""
        return '像家一样温暖'