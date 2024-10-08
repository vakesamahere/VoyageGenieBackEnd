import json

import requests

from ..flight import *

from ..weather import get_weather_info
from ..entertainment import *
from ..nav import *
from ..hotel import *

def get_city_code(city):
    api_key = "8cbeeb681cf4926a0087edd8b2734c49"
    url = "https://restapi.amap.com/v3/geocode/geo?parameters"
    params = {
        "key": api_key,
        "city": city,
        "address": city,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("geocodes")[0].get("adcode")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


# 旅游情况
def travel_data(city, des_city):
    # 天气
    city_adcode = get_city_code(des_city)
    extensions = "base"  # all/base
    weather_info = get_weather_info(city_adcode, extensions)
    # 交通
    trans = transportation(city, des_city)
    ret = {
        "weather": weather_info,
        "transportation": trans
    }
    return ret

# 娱乐相关 聚合接口
def entertainment_data(des_city):
    place = get_city_num(des_city)
    places = [place]  # 例如，选择一个地点
    placenames = [des_city]  # 对应地点的名称
    scope = random.randint(8,10)  # 景点数量可以控制

    sight_data = sight_items(places, placenames, scope)
    print(json.dumps(sight_data, indent=2, ensure_ascii=False))
    food_items = scrape_food_items(places, placenames, scope)
    print(json.dumps(food_items, indent=2, ensure_ascii=False))
    # 提取 hotel 信息
    ret = {
        "sight": sight_data,
        "food": food_items,
    }
    hotels = []
    for sight in ret.get('sight', {}).get('data',[]):
        hotels.extend(sight.get('hotel', {}).get('hotels', []))
    for food in ret.get('food', {}).get('data',[]):
        hotels.extend(food.get('hotel', {}).get('hotels', []))

    # 组织结果
    output = {
        "sight": sight_data.get('data',[]),
        "food": food_items.get('data',[]),
        "hotel": hotels
    }
    return output

def food_data(des_city, min_, max_):
    start_time = time.time()
    place = get_city_num(des_city)
    places = [place]  # 例如，选择一个地点
    placenames = [des_city]  # 对应地点的名称
    scope = random.randint(min_, max_)  # 景点数量可以控制
    print("food scope" + str(scope))
    food_items = scrape_food_items(places, placenames, scope)
    end_time = time.time()
    # 计算执行时间
    execution_time_ms = (end_time - start_time) * 1000
    print("food_data time:")
    print(execution_time_ms)
    return food_items

def sight_data(des_city, min_, max_):
    start_time = time.time()
    place = get_city_num(des_city)
    places = [place]  # 例如，选择一个地点
    placenames = [des_city]  # 对应地点的名称
    scope = random.randint(min_, max_)  # 景点数量可以控制
    print("sight scope" + str(scope))

    sight_data = sight_items(places, placenames, scope)
    end_time = time.time()
    # 计算执行时间
    execution_time_ms = (end_time - start_time) * 1000
    print("sight_data time:")
    print(execution_time_ms)
    return sight_data
def event_location(event):
    location=loc_info(event)
    return location


def event_route(events):
    event = events[0]
    events.remove(event)
    # 解析events 经纬度数据
    events_loc = get_events_loc(events)
    events_loc.insert(0, loc_info(event))
    # 生成最优路线
    events_loc = generate_optimal_path(events_loc)
    # 生成导航路线方案
    res = get_nav_route(events_loc)
    return res

def event_route_start_with_loc(events):
    # list[dict[str,any]]
    # item:{
    #     'location': location, * ->str x,y
    #     'citycode': citycode, * ->citycode
    #     'address': address, *->address
    # }
    # {'location': '113.978615,22.537872', 'citycode': '0755', 'address':'...'}
    # 生成最优路线
    events = generate_optimal_path(events)
    # 生成导航路线方案
    res = get_nav_route(events)
    return res


def hotel_info(event):
    location=get_hotel_info(event)
    return location


def two_event_route(event1,event2):
    event_location1=loc_info(event1)
    event_location2=loc_info(event2)
    return get_distance_and_transit(event_location1,event_location2)
if __name__=="main":
    events = [
        {
            "city": "深圳",
            "address": "深圳市盐田区盐葵路大梅沙段148号"
        },
        {
            "city": "深圳",
            "address": "深圳市南山区华侨城侨城西路"
        },
        {
            "city": "深圳",
            "address": "深圳市福田区益田路5033号平安金融中心116层"
        },
        {
            "city": "深圳",
            "address": "深圳市南山区华侨城深南大道9003号"
        },
        {
            "city": "深圳",
            "address": "深圳市盐田区大梅沙东部华侨城"
        }
    ]
    print(two_event_route(events[0],events[1]))