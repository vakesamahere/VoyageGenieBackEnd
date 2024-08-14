import time, sys, json
from uuid import UUID
from functools import partial

from crewai import Crew, Process, Task
from langchain_core.outputs import LLMResult
from agents import RedditAgents
from tasks import RedditTasks

from toolbox.get_route import GetRoute
from toolbox.get_event_description import GetEventDescription
# from toolbox.get_events import GetEvents
from toolbox.get_route_go_back import GetRouteGoBack
from toolbox.get_event_g import GetEvents
from toolbox.tools.aggregation import result

from langchain.schema import AgentFinish
from typing import Union, List, Tuple, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing import List, Dict, Any
from pydantic import BaseModel, Field
# from file_io import save_markdown
import logging

# 配置logging
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别为DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到控制台
    ]
)

# 获取一个logger实例
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
load_dotenv()

from langchain_community.llms import Ollama
# from langchain_groq import ChatGroq
from langchain.callbacks.base import BaseCallbackHandler

# 创建一个自定义的回调处理器用于流式输出
class StreamingStdOutCallbackHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end="", flush=True)

class RecordStreamHandler(BaseCallbackHandler):
    def __init__(self,receiver=None) -> None:
        self.receiver = receiver
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.receiver.writer_output+=token
        # print(token, end="", flush=True)

# tool回调处理器
class ToolResultHandler(BaseCallbackHandler):
    def __init__(self,receiver=None,tag="") -> None:
        self.receiver = receiver
        self.tag=tag
        self.max_length = 512
    def on_tool_end(self, output: Any, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        # print("="*1000)
        # print(str(output))
        # print("="*1000)
        if self.receiver:
            #[事件名称]字典字符串
            # self.receiver.event_cache_load(f"[{self.tag}]{str(output)}")
            self.receiver.function_used=True
            if self.tag=='get_events':
                self.receiver.tool_result.append({
                    "info_name":self.tag,
                    "info":str(output)
                })
            output = str(output)
            num_segments = (len(output) + self.max_length - 1) // self.max_length
            self.receiver.event_cache_load(f"[{self.tag}]start")
            for i in range(num_segments):
                segment = output[i * self.max_length:(i + 1) * self.max_length]
                self.receiver.event_cache_load(f"[{self.tag}]{segment}")
            self.receiver.event_cache_load(f"[{self.tag}]end")

        return super().on_tool_end(output, run_id=run_id, parent_run_id=parent_run_id, **kwargs)
    
# 打字机效果回调处理器
class TypewriterStreamHandler(BaseCallbackHandler):
    def __init__(self, delay=0.02,receiver=None,rep='\n'):
        self.delay = delay
        self.last_output_time = 0
        self.receiver=receiver
        self.rep = rep
    
    def receiver_send(self,string:str):
        if not self.receiver:
            print('no receiver')
            return
        self.receiver.cache_load(string.replace('\n',self.rep))
        # self.receiver.cache_load(string)

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        current_time = time.time()
        self.receiver_send(token)
        time_since_last_output = current_time - self.last_output_time

        if time_since_last_output < self.delay:
            time.sleep(self.delay - time_since_last_output)
            
        if token.strip():  # 如果token不是空白字符
            for char in token:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(self.delay)
        elif '\n' in token:  # 如果是换行符
            sys.stdout.write('\n')
            sys.stdout.flush()
            time.sleep(self.delay * 2)  # 在换行时稍微多等一下
        else:  # 其他空白字符
            sys.stdout.write(token)
            sys.stdout.flush()
            pass

        self.last_output_time = time.time()
    
    def on_tool_end(self, output: Any, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        print(output)
        with open('./output/on_tool_end.txt','a',encoding='utf-8') as f:
            f.write(str(output))
        return super().on_tool_end(output, run_id=run_id, parent_run_id=parent_run_id, **kwargs)

total_result_example="""
[{'info_name': 'get_events', 'info': "{'success': True, 'data': {'count': '3', 'infocode': '10000', 'pois': [{'parent': 'B00155KO68', 'address': '东泰路126号上海中心大厦F52层', 'distance': '', 'pcode': '310000', 'adcode': '310115', 'pname': '上海市', 'cityname': '上海市', 'type': '购物服务;专卖店;书店', 'photos': [{'title': '', 'url': 'http://aos-cdn-image.amap.com/sns/ugccomment/69e67027-91ce-46b5-a12a-eb36af4c4c43.jpg'}, {'title': '', 'url': 'https://aos-comment.amap.com/B0G0P9FUWI/comment/0616e7e1b2c54ff5797949d89b99c069_2048_2048_80.jpg'}, {'title': '', 'url': 'https://aos-comment.amap.com/B0G0P9FUWI/comment/2b2c97eb9136a5cfb3c3cad8964214d8_2048_2048_80.jpg'}], 'typecode': '061205', 'adname': '浦东新区', 'citycode': '021', 'name': '朵云书院·旗舰店', 'location': '121.505560,31.233492', 'id': 'B0G0P9FUWI'}, {'parent': 'B00155HB25', 'address': '福州路465号世纪出版大厦', 'distance': '', 'pcode': '310000', 'adcode': '310101', 'pname': '上海市', 'cityname': '上海市', 'type': '购物服务;专卖店;书店', 'photos': [{'title': '', 'url': 'https://aos-comment.amap.com/B0FFLPX4S0/comment/1829a2ff77f17d6f8a6f3ce1748a492f_2048_2048_80.jpg'}, {'title': '', 'url': 'https://aos-comment.amap.com/B0FFLPX4S0/comment/c0f2b81b894a19d8ec609a1caadaadfa_2048_2048_80.jpg'}, {'title': '', 'url': 'http://s-pic.oss-cn-beijing.aliyuncs.com/desensitize/images/publish/9a46f121e0f1c385e372982984e825c7.jpg'}], 'typecode': '061205', 'adname': '黄浦区', 'citycode': '021', 'name': '上海书城(福州路店)', 'location': '121.481388,31.233387', 'id': 'B0FFLPX4S0'}, {'parent': 'B00155M168', 'address': '福州路390号1-7层(近上海书城)', 'distance': '', 'pcode': '310000', 'adcode': '310101', 'pname': '上海市', 'cityname': '上海市', 'type': '购物服务;专卖店;书店', 'photos': [{'title': '', 'url': 'http://store.is.autonavi.com/showpic/1e37636e3c0a2ad30dbe138a71027f96'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/b76cc0397c741f1659553caa52df79fb'}, {'title': '内景图', 'url': 'http://store.is.autonavi.com/showpic/001f08e0e4888e1ec847167d3072bdb3'}], 'typecode': '061205', 'adname': '黄浦区', 'citycode': '021', 'name': '外文书店(福州路总店)', 'location': '121.482951,31.234079', 'id': 'B0FFHK7W1H'}], 'status': '1', 'info': 'OK'}}"}, {'info_name': 'get_events', 'info': "{'success': True, 'data': {'count': '3', 'infocode': '10000', 'pois': [{'parent': '', 'address': '中山东一路', 'distance': '', 'pcode': '310000', 'adcode': '310101', 'pname': '上海市', 'cityname': '上海市', 'type': '风景名胜;风景名胜;风景名胜', 'photos': [{'title': '', 'url': 'http://store.is.autonavi.com/showpic/b9c402b7d34ea98654cc915e567761dd'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/979602e27511b1d60f296d840bcfdbb6'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/e4674179351fd7e93e36a8b34b7f624e'}], 'typecode': '110200', 'adname': '黄浦区', 'citycode': '021', 'name': '外滩', 'location': '121.492156,31.233462', 'id': 'B00155FXB3'}, {'parent': '', 'address': '方浜中路249号', 'distance': '', 'pcode': '310000', 'adcode': '310101', 'pname': '上海市', 'cityname': '上海市', 'type': '风景名胜;风景名胜;寺庙道观', 'photos': [{'title': '上海城隍庙', 'url': 'http://store.is.autonavi.com/showpic/518f824f343115a063effa52ea4cb224'}, {'title': '上海城隍庙', 'url': 'http://store.is.autonavi.com/showpic/50bf816321b8a947476ff9ea84b34f76'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/728cd7ef5fa5dbcb554b121359f0eb11'}], 'typecode': '110205', 'adname': '黄浦区', 'citycode': '021', 'name': '上海城隍庙', 'location': '121.492466,31.225879', 'id': 'B00155FHOA'}, {'parent': '', 'address': '安仁街218号', 'distance': '', 'pcode': '310000', 'adcode': '310101', 'pname': '上海市', 'cityname': '上海市', 'type': '风景名胜;风景名胜;国家级景点', 'photos': [{'title': '', 'url': 'http://store.is.autonavi.com/showpic/faeb0264854cd82fbb315cb2ccacea0f'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/a1ae7c02fc36b06b55307525ce4d692c'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/64f950cea19a60bbca1cdfa056a0d2a1'}], 'typecode': '110202', 'adname': '黄浦区', 'citycode': '021', 'name': '上海豫园', 'location': '121.492497,31.227714', 'id': 'B00155MF55'}], 'status': '1', 'info': 'OK'}}"}, {'info_name': 'get_events', 'info': "{'success': True, 'data': {'count': '3', 'infocode': '10000', 'pois': [{'parent': 'B00155KKQJ', 'address': '南京西路231号人民公园内(芭芭露莎一楼)', 'distance': '', 'pcode': '310000', 'adcode': '310101', 'pname': '上海市', 'cityname': '上海市', 'type': '餐饮服务;外国餐厅;外国餐厅', 'photos': [{'title': '', 'url': 'http://store.is.autonavi.com/showpic/5aad3f8e29e515e07cfb00a5d508bbc9'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/46f5a067dfa9716a08fabea9c1478349'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/5006729441231051d3d42754e6e60a9e'}], 'typecode': '050200', 'adname': '黄浦区', 'citycode': '021', 'name': 'Ministry Of Crab', 'location': '121.471851,31.231344', 'id': 'B0FFME80VA'}, {'parent': 'B00155LVRO', 'address': '南京西路258号人广世茂52+3层', 'distance': '', 'pcode': '310000', 'adcode': '310101', 'pname': '上海市', 'cityname': '上海市', 'type': '餐饮服务;中餐厅;中餐厅', 'photos': [{'title': '', 'url': 'http://store.is.autonavi.com/showpic/4404d831373e3e06a3240e96e4f87e7b'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/581a15380f0dc0211b0e70b1d892647d'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/b4cb19d031a729a6d79095b84a0033f8'}], 'typecode': '050100', 'adname': '黄浦区', 'citycode': '021', 'name': '南京大牌档(人民广场店)', 'location': '121.470807,31.232471', 'id': 'B00157H6IJ'}, {'parent': 'B00151BEEE', 'address': '西藏中路268号来福士广场1F层(人民广场地铁站14号口旁)', 'distance': '', 'pcode': '310000', 'adcode': '310101', 'pname': '上海市', 'cityname': '上海市', 'type': '餐饮服务;快餐厅;肯德基', 'photos': [{'title': '', 'url': 'http://store.is.autonavi.com/showpic/62e8c0ce15bcc103e31e666dae763967'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/ca0873fa3f6320e419ef8fdd9267c922'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/63fa79975a4e5d81e135478fe57db335'}], 'typecode': '050301', 'adname': '黄浦区', 'citycode': '021', 'name': '肯德基(网易严选和平店)', 'location': '121.476255,31.232901', 'id': 'B0FFJBC1US'}], 'status': '1', 'info': 'OK'}}"}, {'info_name': 'get_events', 'info': "{'success': True, 'data': {'count': '3', 'infocode': '10000', 'pois': [{'parent': 'B00155LCPL', 'address': '南期昌路751号林芝大厦F1层', 'distance': '', 'pcode': '310000', 'adcode': '310117', 'pname': '上海市', 'cityname': '上海市', 'type': '住宿服务;宾馆酒店;经济型连锁酒店', 'photos': [{'title': 'Logo', 'url': 'http://store.is.autonavi.com/showpic/dc41441c86f36df42fef90810ba85dc8'}, {'title': '商务间A', 'url': 'http://store.is.autonavi.com/showpic/de1ddab8e426ef63691b3a4e1a34b449'}, {'title': '公共区域', 'url': 'http://store.is.autonavi.com/showpic/e5e5a00f9e9bfa5bf6b31460b564ccd3'}], 'typecode': '100105', 'adname': '松江区', 'citycode': '021', 'name': '锦江之星(上海松江大学城店)', 'location': '121.219589,31.022486', 'id': 'B00155LCPY'}, {'parent': '', 'address': '凯旋北路1555弄2号(金沙江路地铁站1口步行360米)', 'distance': '', 'pcode': '310000', 'adcode': '310107', 'pname': '上海市', 'cityname': '上海市', 'type': '住宿服务;宾馆酒店;经济型连锁酒店', 'photos': [{'title': '酒店外观', 'url': 'http://store.is.autonavi.com/showpic/d097745f73e13da371f589af7b986bfe'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/b937a5a4b1d16ca4dd9d5418a6dfb5b7'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/d2a7e775f14e612ea1afabbf818bce53'}], 'typecode': '100105', 'adname': '普陀区', 'citycode': '021', 'name': '布丁酒店(上海华师大金沙江地铁站店)', 'location': '121.412538,31.228851', 'id': 'B0FFFA1RNQ'}, {'parent': '', 'address': '富水路543号(大宁国际商业区,近万泉路)', 'distance': '', 'pcode': '310000', 'adcode': '310107', 'pname': '上海市', 'cityname': '上海市', 'type': '住宿服务;宾馆酒店;三星级宾馆', 'photos': [{'title': 'Logo', 'url': 'http://store.is.autonavi.com/showpic/03c6f0fa44c25ff664ceb393ee5a1d6d'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/6e960f7da5ff0ab60838f395e7f16c22'}, {'title': '', 'url': 'http://store.is.autonavi.com/showpic/c72495f6e201aa72fae1c302e2f9e379'}], 'typecode': '100104', 'adname': '普陀区', 'citycode': '021', 'name': '芭比伦电竞酒店(上海李子园地铁站店)', 'location': '121.399585,31.272053', 'id': 'B00155NCRE'}], 'status': '1', 'info': 'OK'}}"}, {'info_name': 'text', 'info': 'Thought: 根据用户提供的信息，我已经收集到了三个关键信息：出发地（北京）、目的地（上海）和出发时间（明天）。这些信息足够开始制定旅行计划了。我现在可以开始为用户定制旅行计划。\n\n首先，我需要安排往返方案。\n\nAction: Delegate work to coworker\nAction Input: {"task": "制定北京到上海的往返方案", "context": "用户明天从北京出发去上海旅游，需要安排往返方案。用户喜欢看书，可能会影响旅行安排。请提供具体的交通方式、时间和价格信息。", "coworker": "地区间出行规划师"}\nThought: 非常好，我们已经获得了往返方案。现在我们需要为用户在上海寻找合适的游玩地点、美食和住宿地点。\n\nAction: Delegate work to coworker\nAction Input: {"task": "为喜欢看书的游客推荐上海的游玩地点、美食和住宿地点", "context": "用户明天从北京去上海旅游，喜欢看书。请推荐适合的游玩地点、美食和住宿地点，每类至少3个。请提供每个地点的名称、地址、经纬度和城市代码。", "coworker": "景点寻找专家"}\nThought: 现在我们有了游玩地点、美食和住宿地点的推荐。接下来，我们需要为这些地点制定一个合理的游览路线。\n\nAction: Delegate work to coworker\nAction Input: {"task": "为上海的游玩地点规划路线", "context": "用户明天从北京去上海旅游，喜欢看书。我们有以下推荐地点，请为这些地点规划一个合理的3天游览路线：\n\n游玩地点：\n1. 朵云书院·旗舰店 (121.505560, 31.233492)\n2. 上海书城(福州路店) (121.481388, 31.233387)\n3. 外文书店(福州路总店) (121.482951, 31.234079)\n4. 外滩 (121.492156, 31.233462)\n5. 上海城隍庙 (121.492466, 31.225879)\n6. 上海豫园 (121.492497, 31.227714)\n\n美食地点：\n1. Ministry Of Crab (121.471851, 31.231344)\n2. 南京大牌档(人民广场店) (121.470807, 31.232471)\n3. 肯德基(网易严选和平店) (121.476255, 31.232901)\n\n住宿地点：\n1. 锦江之星(上海松江大学城店) (121.219589, 31.022486)\n2. 布丁酒店(上海华师大金沙江地铁站店) (121.412538, 31.228851)\n3. 芭比伦电竞酒店(上海李子园地铁站店) (121.399585, 31.272053)\n\n请考虑地点之间的距离、交通方式和游览时间，给出详细的路线规划。", "coworker": "微观路线规划师"}\nThought: 现在我们已经收集了所有必要的信息，包括往返方案、游玩地点推荐和路线规划。接下来，我们需要将这些信息整合成一份完整的旅行报告。\n\nAction: Delegate work to coworker\nAction Input: {"task": "撰写一份完整的上海旅行计划报告", "context": "用户明天从北京去上海旅游，喜欢看书。我们已经收集了往返方案、游玩地点推荐和路线规划。请根据这些信息撰写一份详细的旅行报告，包括标题、描述、路线和地点详解。", "coworker": "报告撰写师"}\nThought: 我现在已经收集了所有必要的信息，并且得到了一份完整的旅行报告。这份报告包含了用户所需的所有信息，包括往返方案、游玩地点推荐和详细的路线规划。现在我可以给出最终答案了。\n\nFinal Answer: \n\n文艺青年的上海文化之旅\n\n1. 标题：文艺青年的上海文化之旅\n\n2. 描述：本次旅行计划为期3天，从北京出发前往上海。行程安排围绕上海的文化景点展开，特别适合喜欢看书的文艺青年。主要游览地点包括外滩、豫园、上海城隍庙等富有历史文化底蕴的景点，以及充满文艺气息的书店。此外还安排了品尝上海本地美食的时间，让您在感受文化魅力的同时也能领略上海的饮食文化。\n\n3. 路线：\n\n3.1 第一天：北京到上海，书店与外滩之旅\n\n3.1.1 从北京出发\n- 推荐交通方式：高铁 G1123\n- 出发时间：2024年8月6日 06:56\n- 到达时间：2024年8月6日 12:52\n- 行程时间：约5小时56分钟\n\n3.1.2 抵达上海，入住布丁酒店(上海华师大金沙江地铁站店)\n- 地址：上海市普陀区凯旋北路1555弄2号\n- 从上海虹桥站乘坐地铁3号线或4号线到金沙江路站下车\n\n3.1.3 前往外滩\n- 乘坐地铁2号线或10号线到南京东路站下车，步行约10分钟\n- 地址：上海市黄浦区中山东一路\n- 游览时间：约1-2小时\n\n3.1.4 步行至上海豫园（距离约0.657km）\n- 地址：上海市黄浦区安仁街218号\n- 游览时间：约2小时\n\n3.1.5 步行至上海城隍庙（距离约0.202km）\n- 地址：上海市黄浦区方浜中路249号\n- 游览和午餐时间：约2小时\n\n3.1.6 前往外文书店(福州路总店)\n- 步行或乘坐公共交通（距离约1.781km）\n- 地址：上海市黄浦区福州路390号1-7层\n- 浏览时间：约1-1.5小时\n\n3.1.7 步行至上海书城(福州路店)（距离约0.221km）\n- 地址：上海市黄浦区福州路465号世纪出版大厦\n- 浏览和购书时间：约2小时\n\n3.1.8 晚餐：南京大牌档(人民广场店)\n- 地址：上海市黄浦区南京西路258号人广世茂52+3层\n\n3.1.9 返回酒店休息\n\n3.2 第二天：上海地标与书店探索\n\n3.2.1 前往朵云书院·旗舰店\n- 乘坐地铁2号线到陆家嘴站下车\n- 地址：上海市浦东新区东泰路126号上海中心大厦F52层\n- 浏览和购书时间：约2小时\n\n3.2.2 返回外滩区域\n- 步行或乘坐公共交通（距离约1.253km）\n- 深度游览，拍照时间：约2小时\n\n3.2.3 午餐：Ministry Of Crab\n- 地址：上海市黄浦区南京西路231号人民公园内\n\n3.2.4 步行至肯德基(网易严选和平店)（距离约0.58km）短暂休息\n- 地址：上海市黄浦区西藏中路268号来福士广场1F层\n\n3.2.5 自由活动\n- 可以选择在南京路步行街购物或继续在附近景点游览\n\n3.2.6 返回酒店休息\n\n3.3 第三天：深度文化体验与返程\n\n3.3.1 再次游览上海城隍庙和豫园\n- 体验早晨的不同氛围\n- 游览时间：约2-3小时\n\n3.3.2 在城隍庙小吃街享用午餐，品尝上海特色小吃\n\n3.3.3 返回福州路书店区域\n- 可以选择重游喜欢的书店或探索新的书店\n\n3.3.4 晚餐：南京大牌档(人民广场店)\n- 地址：上海市黄浦区南京西路258号人广世茂52+3层\n\n3.3.5 返程北京\n- 建议选择与去程相似的交通方式，具体时间需要根据您的返程日期查询\n\n4. 地点详解：\n\n4.1 朵云书院·旗舰店\n地址：上海市浦东新区东泰路126号上海中心大厦F52层\n简介：位于上海中心大厦的高层，不仅是一家书店，更是一个集阅读、艺术、文化于一体的空间。在这里，您可以欣赏到壮观的上海全景，同时享受宁静的阅读时光。\n\n4.2 上海书城(福州路店)\n地址：上海市黄浦区福州路465号世纪出版大厦\n简介：这是上海最大的综合性书店之一，藏书丰富，环境舒适。福州路被誉为"中国第一书街"，这里是文化爱好者的天堂。\n\n4.3 外文书店(福州路总店)\n地址：上海市黄浦区福州路390号1-7层\n简介：这是上海最大的外文书店，拥有大量的外文书籍和进口杂志，是学习外语和了解国外文化的好去处。\n\n4.4 外滩\n地址：上海市黄浦区中山东一路\n简介：外滩是上海的标志性景点，汇集了众多风格各异的近代建筑，被誉为"万国建筑博览群"。漫步于此，既可欣赏到江对岸浦东的现代化天际线，又能感受到老上海的历史风貌。\n\n4.5 上海城隍庙\n地址：上海市黄浦区方浜中路249号\n简介：上海城隍庙是上海市区内最大的道教宫观，也是著名的旅游景点。这里不仅有历史悠久的建筑，还有各种上海地方小吃，是体验上海传统文化的好去处。\n\n4.6 上海豫园\n地址：上海市黄浦区安仁街218号\n简介：豫园是江南古典园林的代表作之一，始建于明代。园内亭台楼阁错落有致，假山水池相映成趣，处处体现着中国传统园林的精妙构思。游览豫园，仿佛穿越时空，感受明清时期江南园林的魅力。\n\n希望这份详细的旅行计划能够帮助您充分享受上海之旅，感受这座城市丰富的文化底蕴和现代魅力。祝您旅途愉快！'}]
"""

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

format_json = """
        {
        title: string;
        cover: string;
        text: string;
        routes: {
            events: { 
            name: string;
            description: string;
            images: string[];
            }[];
        }[];
        }
        """
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

def run_crew(receiver,msg,rep='\n',testing=False):
    def gen_post(infomation):
        agent=agents.post_writer(llm_no_post)
        print(f'json_writer loaded')

        print("loading task")
        task = Task(
            description="""根据背景信息：{info}.生成一个旅游攻略帖子。图片字段一定不能留空！！""",
            agent=agent,
            expected_output="""JSON format with keys: {format}""",
            llm=llm_no_post
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
        r=crew.kickoff(inputs={
            "format":format_json,
            "info":str(infomation)
        })
        print(f"=============\n\n\n{r.raw}")
        max_length=512
        output=r.raw
        tag='gen_post'
        num_segments = (len(output) + max_length - 1) // max_length
        receiver.event_cache_load(f"[{tag}]start")
        for i in range(num_segments):
            segment = output[i * max_length:(i + 1) * max_length]
            receiver.event_cache_load(f"[{tag}]{segment.replace('\n',rep)}")
        receiver.event_cache_load(f"[{tag}]end")
        # with open('./output/json_output.txt','w',encoding='utf-8') as f:
        #     f.write(r.raw)
        # return r

    print('receiver loading')
    print('receiver loaded')

    print('LLM loading')
    # llm = ChatOpenAI(
    #     model="deepseek-chat", 
    #     verbose=True, 
    #     temperature = 0,
    #     streaming=True,
    #     max_tokens=4096,
    #     callbacks=[TypewriterStreamHandler(delay=0.02,receiver=receiver)]
    #     )
    # print(f'base_url: {llm.openai_api_base}')
    llm = ChatAnthropic(
        model="claude-3-5-sonnet@20240620", 
        verbose=True, 
        temperature = 0,
        top_p=0.9,
        max_tokens=4096,
        streaming=True,
        callbacks=[TypewriterStreamHandler(delay=0.01, receiver=receiver,rep=rep)]
    )
    llm_record = ChatAnthropic(
        model="claude-3-5-sonnet@20240620", 
        verbose=True, 
        temperature = 0,
        top_p=0.9,
        max_tokens=4096,
        streaming=True,
        callbacks=[TypewriterStreamHandler(delay=0.01, receiver=receiver,rep=rep),RecordStreamHandler(receiver=receiver)]
    )
    llm_no_post = ChatAnthropic(
        model="claude-3-5-sonnet@20240620", 
        verbose=True, 
        temperature = 0,
        top_p=0.9,
        max_tokens=4096,
        streaming=True
    )
    print('LLM loaded')

    print('agents loading')
    agents = RedditAgents()
    print(f'agent loaded')
    print('tasks loading')
    tasks = RedditTasks()
    print(f'tasks loaded')

    def crew():
        print('loading each agent')
        manager = agents.manager(llm_record)
        print(f'manager loaded')
        event_finder=agents.eventFinder(llm,[
                GetEvents(
                    callbacks=[ToolResultHandler(receiver=receiver,tag='get_events')]
                    # receiver
                ),
                # SearchTools.search_internet,
                # BrowserTools.scrape_and_summarize_website
            ])
        print(f'event_finer loaded')
        event_teller=agents.eventTeller(llm,[GetEventDescription()])
        print(f'event_teller loaded')
        route_planner=agents.routePlanner(llm,[GetRoute(
            callbacks=[ToolResultHandler(receiver=receiver,tag='get_route')]
            # receiver
            )])
        print(f'route_planner loaded')
        go_back_planner=agents.gobackPlanner(llm,[GetRouteGoBack(
            callbacks=[ToolResultHandler(receiver=receiver,tag='get_route_go_back')]
            # receiver
            )])
        print(f'go_back_planner loaded')
        writer=agents.writer(llm)
        print(f'writer loaded')
        friend=agents.friend(llm)
        print(f'friend loaded')

        print('loading each task')
        # task_talk_with_user = tasks.talk_with_user(agent=talker)
        # print(f'task_talk_with_user loaded')
        task_get_events = tasks.get_events(agent=event_finder,context=[
            #task_talk_with_user
            ])
        print(f'task_get_events loaded')
        task_get_route = tasks.get_route(agent=route_planner,context=[
            task_get_events,
            #task_talk_with_user
            ])
        print(f'task_get_route loaded')
        task_get_route_go_back = tasks.get_route_go_back(agent=go_back_planner,context=[
            #task_talk_with_user
            ])
        print(f'task_get_route_go_back loaded')
        task_get_desc = tasks.get_event_description(agent=event_teller,context=[
            task_get_events,
            #task_talk_with_user
            ])
        print(f'task_get_event_desc loaded')
        task1 = tasks.all(
            agent=writer,
            context=[
                #task_talk_with_user,
                task_get_events,
                task_get_desc,
                task_get_route,
                task_get_route_go_back
                ]
        )
        print(f'task_all loaded')
        # Create a new Crew instance
        print('loading crew')
        crew = Crew(
            agents=[
                #talker,
                event_finder,
                # event_teller,
                route_planner,
                go_back_planner,
                writer,
                ],
            tasks=[
                #task_talk_with_user,
                # task_get_events,
                # task_get_route_go_back,
                # task_get_route,
                # task_get_desc,
                task1,
                ],
            manager_agent=manager,
            process=Process.hierarchical
            # memory=True,
            # embedder={
            #     "provider": "openai",
            #     "config":{
            #         "model": 'text-multilingual-embedding-002'
            #     }
            # }

            # process=Process.hierarchical,
            # manager_llm=llm,
            # step_callback=lambda x: print_agent_output(x,"Reddit Agent")
        )
        print(f'crew loaded\n{crew}')
        return crew
    print('crew kicking off...')
    # Kick of the crew
    # history="user: 明天从北京去上海玩\n"
    # while True:
    #     results = crew().kickoff(inputs={
    #         "city_from":"",
    #         "city_to": "",
    #         "history":history
    #         })
    #     history+=f"AI:{results.raw}\n"
    #     new_input=input("chat with AI: ")
    #     history+=f"user:{new_input}\n"
    #     print(f"history:{history}")
    history=msg
    receiver.event_cache_load('[start]')
    if not testing:
        results = crew().kickoff(inputs={
            "city_from":"",
            "city_to": "",
            "history":history
            })
        print(f'finish \n {results.raw}')
        receiver.tool_result.append({
            "info_name":"text",
            "info":receiver.writer_output
        })
        infomation = str(receiver.tool_result)
        with open('./output/total_result.txt','w',encoding='utf-8') as f:
            f.write(infomation)
        if receiver.function_used:
            gen_post(infomation)
    else:
        gen_post(total_result_example)

    # gen_post(infomation)

    # with open('./output/total_result.txt','r',encoding='utf-8') as f:
    #     res=f.read()
    # gen_post(res)

    # receiver.event_cache_load('[end]')
    receiver.finish = True
    print("Crew work results:")
    # print(results)
    return ''

if __name__ == "__main__":
    import server
    run_crew(server.Receiver(),'明天从北京去上海玩，喜欢看书')