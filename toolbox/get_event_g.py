"""Tool for the VoyageGenie"""
import json
from typing import Optional, Type, List, Any, Dict

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
import requests,os

from dotenv import load_dotenv
load_dotenv()

class GetEventsSchema(BaseModel):
    """Input"""
    keywords: str = Field(..., description="需要被检索的地点文本信息。规则：  只支持一个关键字,若不指定 city，并且搜索的为泛词（例如“美食”）的情况下，返回的内容为城市列表以及此城市内有多少结果符合要求。（keywords 或者 types 二选一必填）")
    types: str = Field(None, description="""指定地点类型，多个关键字用‘|’分隔。可选值：分类代码 或 汉字（若用汉字，请严格按照附件
                       之中的汉字填写）分类代码由六位数字组成，一共分为三个部分，前两个数字代表大类；中间两个数字代表中类；最后两个数字代表小类。若指定了某个大类，则所属的中类、小类都会被显示。例如：010000为汽车服务（大类）;010100为加油站（中类）;010101为中国石化（小类）;010900为汽车租赁（中类）;010901为汽车租赁还车（小类）。当指定010000，则010100等中类、010101等小类会被包含，当指定010900，则010901等小类会被包含。
                       （keywords 或者 types 二选一必填）
                       POI 分类编码表：
                       类型编码(你可选择的输入)	大类	中类	小类
050000	餐饮服务	餐饮相关场所	餐饮相关
050100	餐饮服务	中餐厅	中餐厅
050101	餐饮服务	中餐厅	综合酒楼
050102	餐饮服务	中餐厅	四川菜(川菜)
050103	餐饮服务	中餐厅	广东菜(粤菜)
050104	餐饮服务	中餐厅	山东菜(鲁菜)
050105	餐饮服务	中餐厅	江苏菜
050106	餐饮服务	中餐厅	浙江菜
050107	餐饮服务	中餐厅	上海菜
050108	餐饮服务	中餐厅	湖南菜(湘菜)
050109	餐饮服务	中餐厅	安徽菜(徽菜)
050110	餐饮服务	中餐厅	福建菜
050111	餐饮服务	中餐厅	北京菜
050112	餐饮服务	中餐厅	湖北菜(鄂菜)
050113	餐饮服务	中餐厅	东北菜
050114	餐饮服务	中餐厅	云贵菜
050115	餐饮服务	中餐厅	西北菜
050116	餐饮服务	中餐厅	老字号
050117	餐饮服务	中餐厅	火锅店
050118	餐饮服务	中餐厅	特色/地方风味餐厅
050119	餐饮服务	中餐厅	海鲜酒楼
050120	餐饮服务	中餐厅	中式素菜馆
050121	餐饮服务	中餐厅	清真菜馆
050122	餐饮服务	中餐厅	台湾菜
050123	餐饮服务	中餐厅	潮州菜
050200	餐饮服务	外国餐厅	外国餐厅
050201	餐饮服务	外国餐厅	西餐厅(综合风味)
050202	餐饮服务	外国餐厅	日本料理
050203	餐饮服务	外国餐厅	韩国料理
050204	餐饮服务	外国餐厅	法式菜品餐厅
050205	餐饮服务	外国餐厅	意式菜品餐厅
050206	餐饮服务	外国餐厅	泰国/越南菜品餐厅
050207	餐饮服务	外国餐厅	地中海风格菜品
050208	餐饮服务	外国餐厅	美式风味
050209	餐饮服务	外国餐厅	印度风味
050210	餐饮服务	外国餐厅	英国式菜品餐厅
050211	餐饮服务	外国餐厅	牛扒店(扒房)
050212	餐饮服务	外国餐厅	俄国菜
050213	餐饮服务	外国餐厅	葡国菜
050214	餐饮服务	外国餐厅	德国菜
050215	餐饮服务	外国餐厅	巴西菜
050216	餐饮服务	外国餐厅	墨西哥菜
050217	餐饮服务	外国餐厅	其它亚洲菜
050300	餐饮服务	快餐厅	快餐厅
050301	餐饮服务	快餐厅	肯德基
050302	餐饮服务	快餐厅	麦当劳
050303	餐饮服务	快餐厅	必胜客
050304	餐饮服务	快餐厅	永和豆浆
050305	餐饮服务	快餐厅	茶餐厅
050306	餐饮服务	快餐厅	大家乐
050307	餐饮服务	快餐厅	大快活
050308	餐饮服务	快餐厅	美心
050309	餐饮服务	快餐厅	吉野家
050310	餐饮服务	快餐厅	仙跡岩
050311	餐饮服务	快餐厅	呷哺呷哺
050400	餐饮服务	休闲餐饮场所	休闲餐饮场所
050500	餐饮服务	咖啡厅	咖啡厅
050501	餐饮服务	咖啡厅	星巴克咖啡
050502	餐饮服务	咖啡厅	上岛咖啡
050503	餐饮服务	咖啡厅	Pacific Coffee Company
050504	餐饮服务	咖啡厅	巴黎咖啡店
050600	餐饮服务	茶艺馆	茶艺馆
050700	餐饮服务	冷饮店	冷饮店
050800	餐饮服务	糕饼店	糕饼店
050900	餐饮服务	甜品店	甜品店
060000	购物服务	购物相关场所	购物相关场所
060100	购物服务	商场	商场
060101	购物服务	商场	购物中心
060102	购物服务	商场	普通商场
060103	购物服务	商场	免税品店
060200	购物服务	便民商店/便利店	便民商店/便利店
060201	购物服务	便民商店/便利店	7-ELEVEn便利店
060202	购物服务	便民商店/便利店	OK便利店
060300	购物服务	家电电子卖场	家电电子卖场
060301	购物服务	家电电子卖场	综合家电商场
060302	购物服务	家电电子卖场	国美
060303	购物服务	家电电子卖场	大中
060304	购物服务	家电电子卖场	苏宁
060305	购物服务	家电电子卖场	手机销售
060306	购物服务	家电电子卖场	数码电子
060307	购物服务	家电电子卖场	丰泽
060308	购物服务	家电电子卖场	苏宁镭射
060400	购物服务	超级市场	超市
060401	购物服务	超级市场	家乐福
060402	购物服务	超级市场	沃尔玛
060403	购物服务	超级市场	华润
060404	购物服务	超级市场	北京华联
060405	购物服务	超级市场	上海华联
060406	购物服务	超级市场	麦德龙
060407	购物服务	超级市场	乐天玛特
060408	购物服务	超级市场	华堂
060409	购物服务	超级市场	卜蜂莲花
060411	购物服务	超级市场	屈臣氏
060413	购物服务	超级市场	惠康超市
060414	购物服务	超级市场	百佳超市
060415	购物服务	超级市场	万宁超市
060500	购物服务	花鸟鱼虫市场	花鸟鱼虫市场
060501	购物服务	花鸟鱼虫市场	花卉市场
060502	购物服务	花鸟鱼虫市场	宠物市场
060600	购物服务	家居建材市场	家居建材市场
060601	购物服务	家居建材市场	家具建材综合市场
060602	购物服务	家居建材市场	家具城
060603	购物服务	家居建材市场	建材五金市场
060604	购物服务	家居建材市场	厨卫市场
060605	购物服务	家居建材市场	布艺市场
060606	购物服务	家居建材市场	灯具瓷器市场
060700	购物服务	综合市场	综合市场
060701	购物服务	综合市场	小商品市场
060702	购物服务	综合市场	旧货市场
060703	购物服务	综合市场	农副产品市场
060704	购物服务	综合市场	果品市场
060705	购物服务	综合市场	蔬菜市场
060706	购物服务	综合市场	水产海鲜市场
060800	购物服务	文化用品店	文化用品店
060900	购物服务	体育用品店	体育用品店
060901	购物服务	体育用品店	李宁专卖店
060902	购物服务	体育用品店	耐克专卖店
060903	购物服务	体育用品店	阿迪达斯专卖店
060904	购物服务	体育用品店	锐步专卖店
060905	购物服务	体育用品店	彪马专卖店
060906	购物服务	体育用品店	高尔夫用品店
060907	购物服务	体育用品店	户外用品
061000	购物服务	特色商业街	特色商业街
061001	购物服务	特色商业街	步行街
061100	购物服务	服装鞋帽皮具店	服装鞋帽皮具店
061101	购物服务	服装鞋帽皮具店	品牌服装店
061102	购物服务	服装鞋帽皮具店	品牌鞋店
061103	购物服务	服装鞋帽皮具店	品牌皮具店
061104	购物服务	服装鞋帽皮具店	品牌箱包店
061200	购物服务	专卖店	专营店
061201	购物服务	专卖店	古玩字画店
061202	购物服务	专卖店	珠宝首饰工艺品
061203	购物服务	专卖店	钟表店
061204	购物服务	专卖店	眼镜店
061205	购物服务	专卖店	书店
061206	购物服务	专卖店	音像店
061207	购物服务	专卖店	儿童用品店
061208	购物服务	专卖店	自行车专卖店
061209	购物服务	专卖店	礼品饰品店
061210	购物服务	专卖店	烟酒专卖店
061211	购物服务	专卖店	宠物用品店
061212	购物服务	专卖店	摄影器材店
061213	购物服务	专卖店	宝马生活方式
061214	购物服务	专卖店	土特产专卖店
061300	购物服务	特殊买卖场所	特殊买卖场所
061301	购物服务	特殊买卖场所	拍卖行
061302	购物服务	特殊买卖场所	典当行
061400	购物服务	个人用品/化妆品店	其它个人用品店
061401	购物服务	个人用品/化妆品店	莎莎
080000	体育休闲服务	体育休闲服务场所	体育休闲服务场所
080100	体育休闲服务	运动场馆	运动场所
080101	体育休闲服务	运动场馆	综合体育馆
080102	体育休闲服务	运动场馆	保龄球馆
080103	体育休闲服务	运动场馆	网球场
080104	体育休闲服务	运动场馆	篮球场馆
080105	体育休闲服务	运动场馆	足球场
080106	体育休闲服务	运动场馆	滑雪场
080107	体育休闲服务	运动场馆	溜冰场
080108	体育休闲服务	运动场馆	户外健身场所
080109	体育休闲服务	运动场馆	海滨浴场
080110	体育休闲服务	运动场馆	游泳馆
080111	体育休闲服务	运动场馆	健身中心
080112	体育休闲服务	运动场馆	乒乓球馆
080113	体育休闲服务	运动场馆	台球厅
080114	体育休闲服务	运动场馆	壁球场
080115	体育休闲服务	运动场馆	马术俱乐部
080116	体育休闲服务	运动场馆	赛马场
080117	体育休闲服务	运动场馆	橄榄球场
080118	体育休闲服务	运动场馆	羽毛球场
080119	体育休闲服务	运动场馆	跆拳道场馆
080200	体育休闲服务	高尔夫相关	高尔夫相关
080201	体育休闲服务	高尔夫相关	高尔夫球场
080202	体育休闲服务	高尔夫相关	高尔夫练习场
080300	体育休闲服务	娱乐场所	娱乐场所
080301	体育休闲服务	娱乐场所	夜总会
080302	体育休闲服务	娱乐场所	KTV
080303	体育休闲服务	娱乐场所	迪厅
080304	体育休闲服务	娱乐场所	酒吧
080305	体育休闲服务	娱乐场所	游戏厅
080306	体育休闲服务	娱乐场所	棋牌室
080307	体育休闲服务	娱乐场所	博彩中心
080308	体育休闲服务	娱乐场所	网吧
080400	体育休闲服务	度假疗养场所	度假疗养场所
080401	体育休闲服务	度假疗养场所	度假村
080402	体育休闲服务	度假疗养场所	疗养院
080500	体育休闲服务	休闲场所	休闲场所
080501	体育休闲服务	休闲场所	游乐场
080502	体育休闲服务	休闲场所	垂钓园
080503	体育休闲服务	休闲场所	采摘园
080504	体育休闲服务	休闲场所	露营地
080505	体育休闲服务	休闲场所	水上活动中心
080600	体育休闲服务	影剧院	影剧院相关
080601	体育休闲服务	影剧院	电影院
080602	体育休闲服务	影剧院	音乐厅
080603	体育休闲服务	影剧院	剧场
100000	住宿服务	住宿服务相关	住宿服务相关
100100	住宿服务	宾馆酒店	宾馆酒店
100101	住宿服务	宾馆酒店	奢华酒店
100102	住宿服务	宾馆酒店	五星级宾馆
100103	住宿服务	宾馆酒店	四星级宾馆
100104	住宿服务	宾馆酒店	三星级宾馆
100105	住宿服务	宾馆酒店	经济型连锁酒店
100200	住宿服务	旅馆招待所	旅馆招待所
100201	住宿服务	旅馆招待所	青年旅舍
110000	风景名胜	风景名胜相关	旅游景点
110100	风景名胜	公园广场	公园广场
110101	风景名胜	公园广场	公园
110102	风景名胜	公园广场	动物园
110103	风景名胜	公园广场	植物园
110104	风景名胜	公园广场	水族馆
110105	风景名胜	公园广场	城市广场
110106	风景名胜	公园广场	公园内部设施
110200	风景名胜	风景名胜	风景名胜
110201	风景名胜	风景名胜	世界遗产
110202	风景名胜	风景名胜	国家级景点
110203	风景名胜	风景名胜	省级景点
110204	风景名胜	风景名胜	纪念馆
110205	风景名胜	风景名胜	寺庙道观
110206	风景名胜	风景名胜	教堂
110207	风景名胜	风景名胜	回教寺
110208	风景名胜	风景名胜	海滩
110209	风景名胜	风景名胜	观景点
110210	风景名胜	风景名胜	红色景区
120000	商务住宅	商务住宅相关	商务住宅相关
120100	商务住宅	产业园区	产业园区
120200	商务住宅	楼宇	楼宇相关
120201	商务住宅	楼宇	商务写字楼
120202	商务住宅	楼宇	工业大厦建筑物
120203	商务住宅	楼宇	商住两用楼宇
120300	商务住宅	住宅区	住宅区
120301	商务住宅	住宅区	别墅
120302	商务住宅	住宅区	住宅小区
120303	商务住宅	住宅区	宿舍
120304	商务住宅	住宅区	社区中心
140000	科教文化服务	科教文化场所	科教文化场所
140100	科教文化服务	博物馆	博物馆
140101	科教文化服务	博物馆	奥迪博物馆
140102	科教文化服务	博物馆	梅赛德斯-奔驰博物馆
140200	科教文化服务	展览馆	展览馆
140201	科教文化服务	展览馆	室内展位
140300	科教文化服务	会展中心	会展中心
140400	科教文化服务	美术馆	美术馆
140500	科教文化服务	图书馆	图书馆
140600	科教文化服务	科技馆	科技馆
140700	科教文化服务	天文馆	天文馆
140800	科教文化服务	文化宫	文化宫
140900	科教文化服务	档案馆	档案馆
141000	科教文化服务	文艺团体	文艺团体
141100	科教文化服务	传媒机构	传媒机构
141101	科教文化服务	传媒机构	电视台
141102	科教文化服务	传媒机构	电台
141103	科教文化服务	传媒机构	报社
141104	科教文化服务	传媒机构	杂志社
141105	科教文化服务	传媒机构	出版社
141200	科教文化服务	学校	学校
141201	科教文化服务	学校	高等院校
141202	科教文化服务	学校	中学
141203	科教文化服务	学校	小学
141204	科教文化服务	学校	幼儿园
141205	科教文化服务	学校	成人教育
141206	科教文化服务	学校	职业技术学校
141207	科教文化服务	学校	学校内部设施
141300	科教文化服务	科研机构	科研机构
141400	科教文化服务	培训机构	培训机构
141500	科教文化服务	驾校	驾校
150000	交通设施服务	交通服务相关	交通服务相关
150100	交通设施服务	机场相关	机场相关
150101	交通设施服务	机场相关	候机室
150102	交通设施服务	机场相关	摆渡车站
150104	交通设施服务	机场相关	飞机场
150105	交通设施服务	机场相关	机场出发/到达
150106	交通设施服务	机场相关	直升机场
150107	交通设施服务	机场相关	机场货运处
150200	交通设施服务	火车站	火车站
150201	交通设施服务	火车站	候车室
150202	交通设施服务	火车站	进站口/检票口
150203	交通设施服务	火车站	出站口
150204	交通设施服务	火车站	站台
150205	交通设施服务	火车站	售票
150206	交通设施服务	火车站	退票
150207	交通设施服务	火车站	改签
150208	交通设施服务	火车站	公安制证
150209	交通设施服务	火车站	票务相关
150210	交通设施服务	火车站	货运火车站
150300	交通设施服务	港口码头	港口码头
150301	交通设施服务	港口码头	客运港
150302	交通设施服务	港口码头	车渡口
150303	交通设施服务	港口码头	人渡口
150304	交通设施服务	港口码头	货运港口码头
150305	交通设施服务	港口码头	进港
150306	交通设施服务	港口码头	出港
150307	交通设施服务	港口码头	候船室
150400	交通设施服务	长途汽车站	长途汽车站
150401	交通设施服务	长途汽车站	进站
150402	交通设施服务	长途汽车站	出站
150403	交通设施服务	长途汽车站	候车室
150500	交通设施服务	地铁站	地铁站
150501	交通设施服务	地铁站	出入口
150600	交通设施服务	轻轨站	轻轨站
150700	交通设施服务	公交车站	公交车站相关
150701	交通设施服务	公交车站	旅游专线车站
150702	交通设施服务	公交车站	普通公交站
150703	交通设施服务	公交车站	机场巴士
150704	交通设施服务	公交车站	快速公交站
150705	交通设施服务	公交车站	电车站
150706	交通设施服务	公交车站	智轨车站
150800	交通设施服务	班车站	班车站
150900	交通设施服务	停车场	停车场相关
150903	交通设施服务	停车场	换乘停车场
150904	交通设施服务	停车场	公共停车场
150905	交通设施服务	停车场	专用停车场
150906	交通设施服务	停车场	路边停车场
150907	交通设施服务	停车场	停车场入口
150908	交通设施服务	停车场	停车场出口
150909	交通设施服务	停车场	停车场出入口
151000	交通设施服务	过境口岸	过境口岸
151001	交通设施服务	过境口岸	旅检楼
151002	交通设施服务	过境口岸	出境
151003	交通设施服务	过境口岸	入境
151100	交通设施服务	出租车	出租车
151200	交通设施服务	轮渡站	轮渡站
151300	交通设施服务	索道站	索道站
151400	交通设施服务	上下客区	上下客区
151401	交通设施服务	上下客区	自驾车
151402	交通设施服务	上下客区	出租车
151403	交通设施服务	上下客区	大巴车
151404	交通设施服务	上下客区	网约车
151405	交通设施服务	上下客区	摩托车
170000	公司企业	公司企业	公司企业
170100	公司企业	知名企业	知名企业
170400	公司企业	农林牧渔基地	其它农林牧渔基地
170401	公司企业	农林牧渔基地	渔场
170402	公司企业	农林牧渔基地	农场
170403	公司企业	农林牧渔基地	林场
170404	公司企业	农林牧渔基地	牧场
170405	公司企业	农林牧渔基地	家禽养殖基地
170406	公司企业	农林牧渔基地	蔬菜基地
170407	公司企业	农林牧渔基地	水果基地
170408	公司企业	农林牧渔基地	花卉苗圃基地
190000	地名地址信息	地名地址信息	地名地址信息
190100	地名地址信息	普通地名	普通地名
190101	地名地址信息	普通地名	国家名
190102	地名地址信息	普通地名	省级地名
190103	地名地址信息	普通地名	直辖市级地名
190104	地名地址信息	普通地名	地市级地名
190105	地名地址信息	普通地名	区县级地名
190106	地名地址信息	普通地名	乡镇级地名
190107	地名地址信息	普通地名	街道级地名
190108	地名地址信息	普通地名	村庄级地名
190109	地名地址信息	普通地名	村组级地名
190200	地名地址信息	自然地名	自然地名
190201	地名地址信息	自然地名	海湾海峡
190202	地名地址信息	自然地名	岛屿
190203	地名地址信息	自然地名	山
190204	地名地址信息	自然地名	河流
190205	地名地址信息	自然地名	湖泊
190206	地名地址信息	自然地名	丘陵
190207	地名地址信息	自然地名	山地
190208	地名地址信息	自然地名	冰川
190209	地名地址信息	自然地名	高原
190210	地名地址信息	自然地名	平原
190211	地名地址信息	自然地名	盆地
190212	地名地址信息	自然地名	沙漠
190213	地名地址信息	自然地名	峡谷
190214	地名地址信息	自然地名	溪谷
190215	地名地址信息	自然地名	海沟
190216	地名地址信息	自然地名	半岛
190217	地名地址信息	自然地名	湾
190218	地名地址信息	自然地名	洋
190219	地名地址信息	自然地名	三角洲
190220	地名地址信息	自然地名	山脉
190300	地名地址信息	交通地名	交通地名
190301	地名地址信息	交通地名	道路名
190302	地名地址信息	交通地名	路口名
190303	地名地址信息	交通地名	环岛名
190304	地名地址信息	交通地名	高速路出口
190305	地名地址信息	交通地名	高速路入口
190306	地名地址信息	交通地名	立交桥
190307	地名地址信息	交通地名	桥
190308	地名地址信息	交通地名	城市快速路出口
190309	地名地址信息	交通地名	城市快速路入口
190310	地名地址信息	交通地名	隧道
190311	地名地址信息	交通地名	铁路
190400	地名地址信息	门牌信息	门牌信息
190401	地名地址信息	门牌信息	地名门牌
190402	地名地址信息	门牌信息	道路门牌
190403	地名地址信息	门牌信息	楼栋号
190500	地名地址信息	市中心	城市中心
190600	地名地址信息	标志性建筑物	标志性建筑物
190700	地名地址信息	热点地名	热点地名
200000	公共设施	公共设施	公共设施
200100	公共设施	报刊亭	报刊亭
200200	公共设施	公用电话	公用电话
200300	公共设施	公共厕所	公共厕所
200301	公共设施	公共厕所	男洗手间
200302	公共设施	公共厕所	女洗手间
200303	公共设施	公共厕所	残障洗手间/无障碍洗手间
200304	公共设施	公共厕所	婴儿换洗间/哺乳室/母婴室
200400	公共设施	紧急避难场所	紧急避难场所
220000	事件活动	事件活动	事件活动
220100	事件活动	公众活动	公众活动
220101	事件活动	公众活动	节日庆典
220102	事件活动	公众活动	展会展览
220103	事件活动	公众活动	体育赛事
220104	事件活动	公众活动	文艺演出
220105	事件活动	公众活动	大型会议
220106	事件活动	公众活动	运营活动
220107	事件活动	公众活动	商场活动
220200	事件活动	突发事件	突发事件
220201	事件活动	突发事件	自然灾害
220202	事件活动	突发事件	事故灾难
220203	事件活动	突发事件	城市新闻
220204	事件活动	突发事件	公共卫生事件
220205	事件活动	突发事件	公共社会事件
970000	室内设施	室内设施	室内设施
980000	虚拟数据	虚拟数据	虚拟数据
980100	虚拟数据	虚拟民宿	虚拟民宿
990000	通行设施	通行设施	通行设施
991000	通行设施	建筑物门	建筑物门
991001	通行设施	建筑物门	建筑物正门
991400	通行设施	临街院门	临街院门
991401	通行设施	临街院门	临街院正门
991500	通行设施	虚拟门	虚拟门
991600	通行设施	特殊通道	特殊通道
991601	通行设施	特殊通道	无障碍电梯
                       """)
    region: str = Field(None, description="必须填。搜索区划，如城市名称。")
    page_size: int = Field(10, description="每页展示的数据条数。page_size 的取值1-25")
    page_num: int = Field(1, description="请求的页码。page_num 的取值1-100")

def get_places_from_api(**kwargs) -> Dict[str, Any]:
    """
    调用高德地图API获取地点信息。
    """
    params = kwargs
    params['key'] = os.getenv('API_KEY')
    params['show_fields']='photos'
    # params['city_limit']=True

    response = requests.get('https://restapi.amap.com/v5/place/text', params=params)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == '1':
            print(result.get('info'),result)
        return result
    else:
        print('API请求失败，状态码:', response.status_code)
        return {}
        
def callback_fun(r,content):
    r.event_cache_load(f"[get_events]{json.dumps(content)}")

class GetEvents(BaseTool):
    """在目的地寻找值得一去的地方"""

    name: str = "在目的地寻找值得一去的地方"
    description: str = (
        "一个工具，作用：按照输入、用户偏好搜索地点，可以是游玩地点、餐厅(美食)、住所"
    )
    args_schema: Type[BaseModel] = GetEventsSchema

    def _run(
        self,
        **kwargs,
    ) -> Dict[Any,Any]:
        """Use the tool."""
        search_args = self.args_schema(**kwargs)
        
        # 调用API
        places_data = get_places_from_api(**search_args.dict())

        # 处理返回的数据
        # 这里可以根据实际需要进行数据的处理和转换
        return {
            'success': True,
            'data': places_data
        }
        # 利用高德地图的poi查询用户的偏好

if __name__ == '__main__':
    output = get_places_from_api(
        keywords="故宫",
        types="120000|150000",
        region="北京市",
        # city_limit=True,
        # show_fields="name,address",
        page_size=20,
        page_num=1
    )

    print(output)