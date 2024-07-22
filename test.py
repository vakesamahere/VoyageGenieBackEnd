from tools.aggregation import *

# 测试天气查询功能
def test_weather():
    city = "上海"
    print(f"查询城市：{city} 的天气")
    weather = weather_data(city)
    print("天气查询结果：", weather)

# 测试交通查询功能
def test_travel():
    start_city = "北京"
    des_city = "上海"
    print(f"查询从 {start_city} 到 {des_city} 的交通信息")
    travel_info = travel_data(start_city, des_city)
    print("交通信息查询结果：", travel_info)

# 测试特色小吃查询功能
def test_food():
    des_city = "成都"
    min_count = 1
    max_count = 5
    print(f"查询 {des_city} 的特色小吃，数量在 {min_count} 到 {max_count} 之间")
    food_list = food_data(des_city, min_count, max_count)
    print("特色小吃查询结果：", food_list)

# 测试旅游景点查询功能
def test_sight():
    des_city = "杭州"
    min_count = 1
    max_count = 3
    print(f"查询 {des_city} 的旅游景点，数量在 {min_count} 到 {max_count} 之间")
    sight_list = sight_data(des_city, min_count, max_count)
    print("旅游景点查询结果：", sight_list)

# 测试景点经纬度坐标查询功能
def test_event_location():
    event = {"city": "上海", "address": "同济大学"}
    print(f"查询 {event['city']} 的 {event['address']} 经纬度坐标")
    location_info = event_location(event)
    print("景点经纬度坐标查询结果：", location_info)

# 测试路线规划功能
def test_event_route():
    events = [
        {"city": "北京", "address": "北京市延庆区G6京藏高速58号出口"},
        {"city": "北京", "address": "北京市西城区前海西街17号"}
    ]
    print("查询以下景点之间的路线规划：")
    for event in events:
        print(f"{event['city']} - {event['address']}")
    route_plan = event_route(events)
    print("路线规划结果：", route_plan)

# 主函数，执行测试
def main():
    print('='*50+'天气查询'+'='*50)
    test_weather()

    print('='*50+'往返路线'+'='*50)
    test_travel()

    print('='*50+'食物查询'+'='*50)
    test_food()
    
    print('='*50+'景点查询'+'='*50)
    test_sight()
    
    print('='*50+'地点导航'+'='*50)
    test_event_location()
    
    print('='*50+'路线规划'+'='*50)
    test_event_route()

if __name__ == "__main__":
    main()