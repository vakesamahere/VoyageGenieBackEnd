# Tools 文件夹说明文档

## result.py 方法说明

### `get_city_code(city)`
- **功能**: 根据城市名称获取城市代码。
- **参数**:
  - `city` (str): 城市名称。
- **返回值**:
  - (str): 城市代码。

### `travel_data(city, des_city)`
- **功能**: 获取两个城市之间的旅游数据，包括交通信息。
- **参数**:
  - `city` (str): 出发城市。
  - `des_city` (str): 目的地城市。
- **返回值**:
  - (dict): 包含交通信息的字典。

### `weather_data(city)`
- **功能**: 获取指定城市的天气信息。
- **参数**:
  - `city` (str): 城市名称。
- **返回值**:
  - (dict): 包含天气信息的字典。

### `entertainment_data(des_city)`
- **功能**: 获取指定城市的娱乐数据，包括景点和美食。
- **参数**:
  - `des_city` (str): 目的地城市。
- **返回值**:
  - (dict): 包含景点和美食信息的字典。

### `food_data(des_city, min_, max_)`
- **功能**: 获取指定城市的美食数据。
- **参数**:
  - `des_city` (str): 目的地城市。
  - `min_` (int): 最小数量。
  - `max_` (int): 最大数量。
- **返回值**:
  - (dict): 包含美食信息的字典。

### `sight_data(des_city, min_, max_)`
- **功能**: 获取指定城市的景点数据。
- **参数**:
  - `des_city` (str): 目的地城市。
  - `min_` (int): 最小数量。
  - `max_` (int): 最大数量。
- **返回值**:
  - (dict): 包含景点信息的字典。

### `event_location(event)`
- **功能**: 获取事件地点的详细信息。
- **参数**:
  - `event` (dict): 包含城市和地址的事件信息。
- **返回值**:
  - (dict): 包含地点详细信息的字典。

### `event_route(events)`
- **功能**: 生成事件的最优路线。
- **参数**:
  - `events` (list): 包含多个事件信息的列表。
- **返回值**:
  - (dict): 包含最优路线信息的字典。
