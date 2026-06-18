# 和风天气 API 全量文档

> 来源：https://dev.qweather.com/docs/api/
> 生成时间：2026-05-07

## 目录

- [GeoAPI](#geoapi)
  - [城市搜索](#城市搜索)
  - [热门城市查询](#热门城市查询)
  - [POI搜索](#poi搜索)
  - [POI范围搜索](#poi范围搜索)
- [天气预报](#天气预报)
  - [实时天气](#实时天气)
  - [每日天气预报](#每日天气预报)
  - [逐小时天气预报](#逐小时天气预报)
  - [格点实时天气](#格点实时天气)
  - [格点每日天气预报](#格点每日天气预报)
  - [格点逐小时天气预报](#格点逐小时天气预报)
- [分钟预报](#分钟预报)
  - [分钟级降水](#分钟级降水)
- [预警](#预警)
  - [实时天气预警](#实时天气预警)
- [天气指数](#天气指数)
  - [天气指数预报](#天气指数预报)
- [空气质量](#空气质量)
  - [实时空气质量](#实时空气质量)
  - [空气质量小时预报](#空气质量小时预报)
  - [空气质量每日预报](#空气质量每日预报)
  - [监测站数据](#监测站数据)
- [时光机](#时光机)
  - [天气时光机](#天气时光机)
  - [空气质量时光机](#空气质量时光机)
- [热带气旋（台风）](#热带气旋台风)
  - [台风预报](#台风预报)
  - [台风实况和路径](#台风实况和路径)
  - [台风列表](#台风列表)
- [海洋数据](#海洋数据)
  - [潮汐](#潮汐)
- [太阳辐射](#太阳辐射)
  - [太阳辐射预报](#太阳辐射预报)
- [天文](#天文)
  - [日出日落](#日出日落)
  - [月升月落和月相](#月升月落和月相)
  - [太阳高度角](#太阳高度角)
- [控制台API](#控制台api)
  - [财务汇总](#财务汇总)
  - [请求量统计](#请求量统计)

---

## GeoAPI

和风天气GeoAPI提供全球地理位位置、全球城市搜索服务，支持经纬度坐标反查、多语言、模糊搜索等功能。

天气数据是基于地理位置的数据，因此获取天气之前需要先知道具体的位置信息。和风天气提供一个功能强大的位置信息搜索API服务：GeoAPI。通过GeoAPI，你可获取到需要查询城市或POI的基本信息，包括查询地区的Location ID（你需要这个ID去查询天气），多语言名称、经纬度、时区、海拔、Rank值、归属上级行政区域、所在行政区域等。

### 城市搜索

**接口地址**: `/geo/v2/city/lookup`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | 需要查询地区的名称，支持文字、经度,纬度坐标（十进制，最多支持小数点后两位）、LocationID或Adcode（仅限中国城市）。支持模糊搜索，最少一个汉字或2个字符 |
| adm | string | 否 | 城市的上级行政区划，可设定只在某个行政区划范围内搜索，用于排除重名城市或对结果进行过滤 |
| range | string | 否 | 搜索范围，可设定只在某个国家或地区范围内搜索，需使用ISO 3166国家代码 |
| number | int | 否 | 返回结果的数量，取值范围1-20，默认返回10个结果 |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/geo/v2/city/lookup?location=beij'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| location[].name | string | 地区/城市名称 |
| location[].id | string | 地区/城市ID |
| location[].lat | string | 地区/城市纬度 |
| location[].lon | string | 地区/城市经度 |
| location[].adm2 | string | 地区/城市的上级行政区划名称 |
| location[].adm1 | string | 地区/城市所属一级行政区域 |
| location[].country | string | 地区/城市所属国家名称 |
| location[].tz | string | 地区/城市所在时区 |
| location[].utcOffset | string | 地区/城市目前与UTC时间偏移的小时数 |
| location[].isDst | string | 地区/城市是否当前处于夏令时（1=是，0=否） |
| location[].type | string | 地区/城市的属性 |
| location[].rank | string | 地区评分 |
| location[].fxLink | string | 该地区的天气预报网页链接 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "location": [
    {
      "name": "北京",
      "id": "101010100",
      "lat": "39.90499",
      "lon": "116.40529",
      "adm2": "北京",
      "adm1": "北京市",
      "country": "中国",
      "tz": "Asia/Shanghai",
      "utcOffset": "+08:00",
      "isDst": "0",
      "type": "city",
      "rank": "10",
      "fxLink": "https://www.qweather.com/weather/beijing-101010100.html"
    }
  ],
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

### 热门城市查询

**接口地址**: `/geo/v2/city/top`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| range | string | 否 | 搜索范围，可设定只在某个国家或地区范围内搜索，需使用ISO 3166国家代码 |
| number | int | 否 | 返回结果的数量，取值范围1-20，默认返回10个结果 |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/geo/v2/city/top?number=5&range=cn'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| topCityList[].name | string | 地区/城市名称 |
| topCityList[].id | string | 地区/城市ID |
| topCityList[].lat | string | 地区/城市纬度 |
| topCityList[].lon | string | 地区/城市经度 |
| topCityList[].adm2 | string | 地区/城市的上级行政区划名称 |
| topCityList[].adm1 | string | 地区/城市所属一级行政区域 |
| topCityList[].country | string | 地区/城市所属国家名称 |
| topCityList[].tz | string | 地区/城市所在时区 |
| topCityList[].utcOffset | string | 地区/城市目前与UTC时间偏移的小时数 |
| topCityList[].isDst | string | 地区/城市是否当前处于夏令时（1=是，0=否） |
| topCityList[].type | string | 地区/城市的属性 |
| topCityList[].rank | string | 地区评分 |
| topCityList[].fxLink | string | 该地区的天气预报网页链接 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "topCityList": [
    {
      "name": "北京",
      "id": "101010100",
      "lat": "39.90499",
      "lon": "116.40529",
      "adm2": "北京",
      "adm1": "北京市",
      "country": "中国",
      "tz": "Asia/Shanghai",
      "utcOffset": "+08:00",
      "isDst": "0",
      "type": "city",
      "rank": "10",
      "fxLink": "https://www.qweather.com/weather/beijing-101010100.html"
    }
  ],
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

### POI搜索

**接口地址**: `/geo/v2/poi/lookup`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | 需要查询地区的名称，支持文字、经度,纬度坐标、LocationID或Adcode（仅限中国城市） |
| type | string | 是 | POI类型。可选值：scenic（景点）、TSTA（潮汐站点） |
| city | string | 否 | 选择POI所在城市，可设定只搜索在特定城市内的POI信息 |
| number | int | 否 | 返回结果的数量，取值范围1-20，默认返回10个结果 |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/geo/v2/poi/lookup?type=scenic&location=jings'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| poi[].name | string | POI（兴趣点）名称 |
| poi[].id | string | POI（兴趣点）ID |
| poi[].lat | string | POI（兴趣点）纬度 |
| poi[].lon | string | POI（兴趣点）经度 |
| poi[].adm2 | string | POI的上级行政区划名称 |
| poi[].adm1 | string | POI所属一级行政区域 |
| poi[].country | string | POI所属国家名称 |
| poi[].tz | string | POI所在时区 |
| poi[].utcOffset | string | POI目前与UTC时间偏移的小时数 |
| poi[].isDst | string | POI是否当前处于夏令时（1=是，0=否） |
| poi[].type | string | POI的属性 |
| poi[].rank | string | 地区评分 |
| poi[].fxLink | string | 该地区的天气预报网页链接 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "poi": [
    {
      "name": "景山公园",
      "id": "10101010012A",
      "lat": "39.91999",
      "lon": "116.38999",
      "adm2": "北京",
      "adm1": "北京",
      "country": "中国",
      "tz": "Asia/Shanghai",
      "utcOffset": "+08:00",
      "isDst": "0",
      "type": "scenic",
      "rank": "67",
      "fxLink": "https://www.qweather.com"
    }
  ],
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

### POI范围搜索

**接口地址**: `/geo/v2/poi/range`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | 需要查询地区的以英文逗号分隔的经度,纬度坐标（十进制，最多支持小数点后两位） |
| type | string | 是 | POI类型。可选值：scenic（景点）、TSTA（潮汐站点） |
| radius | int | 否 | 搜索范围，可设置搜索半径，取值范围1-50，单位：公里。默认5公里 |
| number | int | 否 | 返回结果的数量，取值范围1-20，默认返回10个结果 |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/geo/v2/poi/range?location=116.40528,39.90498&type=scenic&radius=10'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| poi[].name | string | POI名称 |
| poi[].id | string | POI ID |
| poi[].lat | string | POI纬度 |
| poi[].lon | string | POI经度 |
| poi[].adm2 | string | POI的上级行政区划名称 |
| poi[].adm1 | string | POI所属一级行政区域 |
| poi[].country | string | POI所属国家名称 |
| poi[].tz | string | POI所在时区 |
| poi[].utcOffset | string | POI与UTC时间偏移的小时数 |
| poi[].isDst | string | POI是否处于夏令时（1=是，0=否） |
| poi[].type | string | POI的属性 |
| poi[].rank | string | 地区评分 |
| poi[].fxLink | string | 天气预报网页链接 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "poi": [
    {
      "name": "故宫博物院",
      "id": "10101010018A",
      "lat": "39.90999985",
      "lon": "116.38999939",
      "adm2": "北京",
      "adm1": "北京",
      "country": "中国",
      "tz": "Asia/Shanghai",
      "utcOffset": "+08:00",
      "isDst": "0",
      "type": "scenic",
      "rank": "67",
      "fxLink": "https://www.qweather.com"
    }
  ],
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

## 天气预报

天气API提供全球20多万个城市的实时天气和预报数据，并支持基于数值模式的天气预报，分辨率达3–5公里，覆盖全球坐标点。

### 实时天气

**接口地址**: `/v7/weather/now`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | 需要查询地区的LocationID或经度,纬度坐标（十进制，最多支持小数点后两位），LocationID可通过GeoAPI获取 |
| lang | string | 否 | 多语言设置 |
| unit | string | 否 | 数据单位设置，可选值：m（公制单位，默认）、i（英制单位） |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/weather/now?location=101010100'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 当前数据的响应式页面链接 |
| now.obsTime | string | 数据观测时间 |
| now.temp | string | 温度，默认单位：摄氏度 |
| now.feelsLike | string | 体感温度，默认单位：摄氏度 |
| now.icon | string | 天气状况的图标代码 |
| now.text | string | 天气状况的文字描述 |
| now.wind360 | string | 风向360角度 |
| now.windDir | string | 风向 |
| now.windScale | string | 风力等级 |
| now.windSpeed | string | 风速，公里/小时 |
| now.humidity | string | 相对湿度，百分比数值 |
| now.precip | string | 过去1小时降水量，默认单位：毫米 |
| now.pressure | string | 大气压强，默认单位：百帕 |
| now.vis | string | 能见度，默认单位：公里 |
| now.cloud | string | 云量，百分比数值。可能为空 |
| now.dew | string | 露点温度。可能为空 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "updateTime": "2020-06-30T22:00+08:00",
  "fxLink": "http://hfx.link/2ax1",
  "now": {
    "obsTime": "2020-06-30T21:40+08:00",
    "temp": "24",
    "feelsLike": "26",
    "icon": "101",
    "text": "多云",
    "wind360": "123",
    "windDir": "东南风",
    "windScale": "1",
    "windSpeed": "3",
    "humidity": "72",
    "precip": "0.0",
    "pressure": "1003",
    "vis": "16",
    "cloud": "10",
    "dew": "21"
  },
  "refer": {
    "sources": ["QWeather", "NMC", "ECMWF"],
    "license": ["QWeather Developers License"]
  }
}
```

---

### 每日天气预报

**接口地址**: `/v7/weather/{days}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| days | string | 是 | 预报天数（路径参数）。可选值：3d（3天）、7d（7天）、10d（10天）、15d（15天）、30d（30天） |
| location | string | 是 | 需要查询地区的LocationID或经度,纬度坐标 |
| lang | string | 否 | 多语言设置 |
| unit | string | 否 | 数据单位设置，可选值：m（公制，默认）、i（英制） |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/weather/3d?location=101010100'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| daily[].fxDate | string | 预报日期 |
| daily[].sunrise | string | 日出时间，高纬度地区可能为空 |
| daily[].sunset | string | 日落时间，高纬度地区可能为空 |
| daily[].moonrise | string | 月升时间，可能为空 |
| daily[].moonset | string | 月落时间，可能为空 |
| daily[].moonPhase | string | 月相名称 |
| daily[].moonPhaseIcon | string | 月相图标代码 |
| daily[].tempMax | string | 预报当天最高温度 |
| daily[].tempMin | string | 预报当天最低温度 |
| daily[].iconDay | string | 白天天气状况图标代码 |
| daily[].textDay | string | 白天天气状况文字描述 |
| daily[].iconNight | string | 夜间天气状况图标代码 |
| daily[].textNight | string | 夜间天气状况文字描述 |
| daily[].wind360Day | string | 白天风向360角度 |
| daily[].windDirDay | string | 白天风向 |
| daily[].windScaleDay | string | 白天风力等级 |
| daily[].windSpeedDay | string | 白天风速，公里/小时 |
| daily[].wind360Night | string | 夜间风向360角度 |
| daily[].windDirNight | string | 夜间风向 |
| daily[].windScaleNight | string | 夜间风力等级 |
| daily[].windSpeedNight | string | 夜间风速，公里/小时 |
| daily[].humidity | string | 相对湿度，百分比 |
| daily[].precip | string | 当天总降水量，默认单位：毫米 |
| daily[].pressure | string | 大气压强，默认单位：百帕 |
| daily[].vis | string | 能见度，默认单位：公里 |
| daily[].cloud | string | 云量，百分比。可能为空 |
| daily[].uvIndex | string | 紫外线强度指数 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "updateTime": "2021-11-15T16:35+08:00",
  "fxLink": "http://hfx.link/2ax1",
  "daily": [
    {
      "fxDate": "2021-11-15",
      "sunrise": "06:58",
      "sunset": "16:59",
      "moonrise": "15:16",
      "moonset": "03:40",
      "moonPhase": "盈凸月",
      "moonPhaseIcon": "803",
      "tempMax": "12",
      "tempMin": "-1",
      "iconDay": "101",
      "textDay": "多云",
      "iconNight": "150",
      "textNight": "晴",
      "wind360Day": "45",
      "windDirDay": "东北风",
      "windScaleDay": "1-2",
      "windSpeedDay": "3",
      "wind360Night": "0",
      "windDirNight": "北风",
      "windScaleNight": "1-2",
      "windSpeedNight": "3",
      "humidity": "65",
      "precip": "0.0",
      "pressure": "1020",
      "vis": "25",
      "cloud": "4",
      "uvIndex": "3"
    }
  ],
  "refer": {
    "sources": ["QWeather", "NMC", "ECMWF"],
    "license": ["QWeather Developers License"]
  }
}
```

---

### 逐小时天气预报

**接口地址**: `/v7/weather/{hours}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| hours | string | 是 | 预报小时数（路径参数）。可选值：24h（24小时）、72h（72小时）、168h（168小时） |
| location | string | 是 | 需要查询地区的LocationID或经度,纬度坐标 |
| lang | string | 否 | 多语言设置 |
| unit | string | 否 | 数据单位设置，可选值：m（公制，默认）、i（英制） |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/weather/24h?location=101010100'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| hourly[].fxTime | string | 预报时间 |
| hourly[].temp | string | 温度，默认单位：摄氏度 |
| hourly[].icon | string | 天气状况图标代码 |
| hourly[].text | string | 天气状况文字描述 |
| hourly[].wind360 | string | 风向360角度 |
| hourly[].windDir | string | 风向 |
| hourly[].windScale | string | 风力等级 |
| hourly[].windSpeed | string | 风速，公里/小时 |
| hourly[].humidity | string | 相对湿度，百分比 |
| hourly[].precip | string | 当前小时累计降水量，默认单位：毫米 |
| hourly[].pop | string | 逐小时预报降水概率，百分比，可能为空 |
| hourly[].pressure | string | 大气压强，默认单位：百帕 |
| hourly[].cloud | string | 云量，百分比。可能为空 |
| hourly[].dew | string | 露点温度。可能为空 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "updateTime": "2021-02-16T13:35+08:00",
  "fxLink": "http://hfx.link/2ax1",
  "hourly": [
    {
      "fxTime": "2021-02-16T15:00+08:00",
      "temp": "2",
      "icon": "100",
      "text": "晴",
      "wind360": "335",
      "windDir": "西北风",
      "windScale": "3-4",
      "windSpeed": "20",
      "humidity": "11",
      "pop": "0",
      "precip": "0.0",
      "pressure": "1025",
      "cloud": "0",
      "dew": "-25"
    }
  ],
  "refer": {
    "sources": ["QWeather", "NMC", "ECMWF"],
    "license": ["QWeather Developers License"]
  }
}
```

---

### 格点实时天气

基于数值模式的天气预报数据，提供全球指定坐标的实时天气，分辨率3-5公里。

**接口地址**: `/v7/grid-weather/now`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | 需要查询地区的以英文逗号分隔的经度,纬度坐标（十进制，最多支持小数点后两位） |
| lang | string | 否 | 多语言设置 |
| unit | string | 否 | 数据单位设置，可选值：m（公制，默认）、i（英制） |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/grid-weather/now?location=116.41,39.92'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| now.obsTime | string | 数据观测时间 |
| now.temp | string | 温度，默认单位：摄氏度 |
| now.icon | string | 天气状况图标代码 |
| now.text | string | 天气状况文字描述 |
| now.wind360 | string | 风向360角度 |
| now.windDir | string | 风向 |
| now.windScale | string | 风力等级 |
| now.windSpeed | string | 风速，公里/小时 |
| now.humidity | string | 相对湿度，百分比 |
| now.precip | string | 过去1小时降水量，默认单位：毫米 |
| now.pressure | string | 大气压强，默认单位：百帕 |
| now.cloud | string | 云量，百分比。可能为空 |
| now.dew | string | 露点温度。可能为空 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "updateTime": "2021-12-16T18:25+08:00",
  "fxLink": "https://www.qweather.com",
  "now": {
    "obsTime": "2021-12-16T10:00+00:00",
    "temp": "-1",
    "icon": "150",
    "text": "晴",
    "wind360": "287",
    "windDir": "西北风",
    "windScale": "2",
    "windSpeed": "10",
    "humidity": "27",
    "precip": "0.0",
    "pressure": "1021",
    "cloud": "0",
    "dew": "-17"
  },
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

### 格点每日天气预报

基于数值模式的天气预报数据，提供全球指定坐标的每日天气预报，分辨率3-5公里。

**接口地址**: `/v7/grid-weather/{days}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| days | string | 是 | 预报天数（路径参数）。可选值：3d（3天）、7d（7天） |
| location | string | 是 | 需要查询地区的经度,纬度坐标 |
| lang | string | 否 | 多语言设置 |
| unit | string | 否 | 数据单位设置，可选值：m（公制，默认）、i（英制） |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/grid-weather/3d?location=116.41,39.92'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| daily[].fxDate | string | 预报日期 |
| daily[].tempMax | string | 预报当天最高温度 |
| daily[].tempMin | string | 预报当天最低温度 |
| daily[].iconDay | string | 白天天气状况图标代码 |
| daily[].textDay | string | 白天天气状况文字描述 |
| daily[].iconNight | string | 夜间天气状况图标代码 |
| daily[].textNight | string | 夜间天气状况文字描述 |
| daily[].wind360Day | string | 白天风向360角度 |
| daily[].windDirDay | string | 白天风向 |
| daily[].windScaleDay | string | 白天风力等级 |
| daily[].windSpeedDay | string | 白天风速，公里/小时 |
| daily[].wind360Night | string | 夜间风向360角度 |
| daily[].windDirNight | string | 夜间风向 |
| daily[].windScaleNight | string | 夜间风力等级 |
| daily[].windSpeedNight | string | 夜间风速，公里/小时 |
| daily[].humidity | string | 相对湿度，百分比 |
| daily[].precip | string | 当天总降水量，默认单位：毫米 |
| daily[].pressure | string | 大气压强，默认单位：百帕 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "updateTime": "2021-12-16T18:30+08:00",
  "fxLink": "https://www.qweather.com",
  "daily": [
    {
      "fxDate": "2021-12-16",
      "tempMax": "2",
      "tempMin": "-7",
      "iconDay": "104",
      "iconNight": "154",
      "textDay": "阴",
      "textNight": "阴",
      "wind360Day": "344",
      "windDirDay": "西北风",
      "windScaleDay": "4-5",
      "windSpeedDay": "9",
      "wind360Night": "304",
      "windDirNight": "西北风",
      "windScaleNight": "4-5",
      "windSpeedNight": "6",
      "humidity": "36",
      "precip": "0.0",
      "pressure": "1026"
    }
  ],
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

### 格点逐小时天气预报

基于数值模式的天气预报数据，提供全球指定坐标的逐小时天气预报，分辨率3-5公里。

**接口地址**: `/v7/grid-weather/{hours}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| hours | string | 是 | 预报小时数（路径参数）。可选值：24h（24小时）、72h（72小时） |
| location | string | 是 | 需要查询地区的经度,纬度坐标 |
| lang | string | 否 | 多语言设置 |
| unit | string | 否 | 数据单位设置，可选值：m（公制，默认）、i（英制） |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/grid-weather/24h?location=116.41,39.92'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| hourly[].fxTime | string | 预报时间 |
| hourly[].temp | string | 温度，默认单位：摄氏度 |
| hourly[].icon | string | 天气状况图标代码 |
| hourly[].text | string | 天气状况文字描述 |
| hourly[].wind360 | string | 风向360角度 |
| hourly[].windDir | string | 风向 |
| hourly[].windScale | string | 风力等级 |
| hourly[].windSpeed | string | 风速，公里/小时 |
| hourly[].humidity | string | 相对湿度，百分比 |
| hourly[].precip | string | 当前小时累计降水量，默认单位：毫米 |
| hourly[].cloud | string | 云量，百分比。可能为空 |
| hourly[].dew | string | 露点温度。可能为空 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "updateTime": "2021-12-16T19:27+08:00",
  "fxLink": "https://www.qweather.com",
  "hourly": [
    {
      "fxTime": "2021-12-16T12:00+00:00",
      "temp": "-2",
      "icon": "150",
      "text": "晴",
      "wind360": "285",
      "windDir": "西北风",
      "windScale": "2",
      "windSpeed": "8",
      "humidity": "30",
      "precip": "0.0",
      "pressure": "1022",
      "cloud": "0",
      "dew": "-17"
    }
  ],
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

## 分钟预报

### 分钟级降水

分钟级降水API（临近预报）支持中国1公里精度的未来2小时每5分钟降雨预报数据。

**接口地址**: `/v7/minutely/5m`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | 需要查询地区的经度,纬度坐标 |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/minutely/5m?location=116.38,39.91'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| summary | string | 分钟降水描述 |
| minutely[].fxTime | string | 预报时间 |
| minutely[].precip | string | 5分钟累计降水量，单位毫米 |
| minutely[].type | string | 降水类型：rain（雨）、snow（雪） |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "updateTime": "2021-12-16T18:55+08:00",
  "fxLink": "https://www.qweather.com",
  "summary": "95分钟后雨就停了",
  "minutely": [
    {
      "fxTime": "2021-12-16T18:55+08:00",
      "precip": "0.15",
      "type": "rain"
    }
  ],
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

## 预警

和风极端天气预警API提供了全球官方发布的极端天气预警服务，覆盖中国及全球国家或地区。

### 实时天气预警

**接口地址**: `/weatheralert/v1/current/{latitude}/{longitude}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| latitude | float | 是 | 所需位置的纬度（路径参数）。十进制，最多支持小数点后两位 |
| longitude | float | 是 | 所需位置的经度（路径参数）。十进制，最多支持小数点后两位 |
| localTime | bool | 否 | 是否返回查询地点的本地时间。true=本地时间，false=UTC时间（默认） |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/weatheralert/v1/current/39.90/116.40'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| metadata.tag | string | 数据标签 |
| metadata.zeroResult | bool | true表示请求成功，但无数据返回 |
| metadata.attributions | array | 数据来源或声明 |
| alerts[].id | string | 预警信息的唯一标识 |
| alerts[].senderName | string | 预警发布机构名称，可能为空 |
| alerts[].issuedTime | string | 原始预警信息生成时间 |
| alerts[].messageType.code | string | 预警信息性质的代码 |
| alerts[].messageType.supersedes | array | 被取代的预警ID列表 |
| alerts[].eventType.name | string | 预警事件类型的名称 |
| alerts[].eventType.code | string | 预警事件类型的代码 |
| alerts[].urgency | string | 紧迫程度，可能为空 |
| alerts[].severity | string | 严重程度 |
| alerts[].certainty | string | 确定性或可信度，可能为空 |
| alerts[].icon | string | 预警对应的图标代码 |
| alerts[].color.code | string | 预警信息的颜色代码 |
| alerts[].color.red | int | 红色分量值（RGBA），0–255 |
| alerts[].color.green | int | 绿色分量值（RGBA），0–255 |
| alerts[].color.blue | int | 蓝色分量值（RGBA），0–255 |
| alerts[].color.alpha | float | 透明度分量值（RGBA），0-1 |
| alerts[].effectiveTime | string | 预警生效时间，可能为空 |
| alerts[].onsetTime | string | 预警事件预计开始时间，可能为空 |
| alerts[].expireTime | string | 预警失效时间 |
| alerts[].headline | string | 预警简要描述或标题 |
| alerts[].description | string | 预警详细描述 |
| alerts[].criteria | string | 触发标准或条件，可能为空 |
| alerts[].instruction | string | 防御指南或行动指导，可能为空 |
| alerts[].responseTypes | array | 应对方式的类型代码，可能为空 |

**响应示例**:

```json
{
  "metadata": {
    "tag": "ec71f87d59c5db45281fecc9f25d136f638ba414ff0a4c4e97258e6d30218aac",
    "zeroResult": false,
    "attributions": [
      "https://developer.qweather.com/attribution.html",
      "当前预警数据可能存在延迟或信息过时，以官方数据发布为准。"
    ]
  },
  "alerts": [
    {
      "id": "202510241119105837988676",
      "senderName": "临桂区气象台",
      "issuedTime": "2025-10-24T11:19+08:00",
      "messageType": { "code": "update", "supersedes": ["202510181140100706230391"] },
      "eventType": { "name": "大风", "code": "1006" },
      "urgency": null,
      "severity": "minor",
      "certainty": null,
      "icon": "1006",
      "color": { "code": "blue", "red": 30, "green": 50, "blue": 205, "alpha": 1 },
      "effectiveTime": "2025-10-24T11:19+08:00",
      "onsetTime": "2025-10-24T11:19+08:00",
      "expireTime": "2025-10-25T11:19+08:00",
      "headline": "临桂区气象台更新大风蓝色预警信号",
      "description": "临桂区气象台24日11时19分继续发布大风蓝色预警信号：预计未来24小时内临桂将出现6级（或阵风7级）以上大风，请做好防范。",
      "criteria": "24小时内可能受大风影响，平均风力可达6级以上，或者阵风7级以上；或者已经受大风影响，平均风力为6～7级，或者阵风7～8级并可能持续。",
      "responseTypes": [],
      "instruction": "1. 政府及有关部门按照职责做好防大风工作。\n2. 关好门窗，加固围板、棚架、广告牌等易被风吹动的搭建物，妥善安置易受大风影响的室外物品，遮盖建筑物资。\n3. 相关水域水上作业和过往船舶采取积极的应对措施，如回港避风或者绕道航行等。\n4. 行人注意尽量少骑自行车，刮风时不要在广告牌、临时搭建物等下面逗留。\n5. 有关部门和单位注意森林、草原等防火。"
    }
  ]
}
```

---

## 天气指数

### 天气指数预报

获取中国和全球城市天气生活指数预报数据。

中国天气生活指数：舒适度指数、洗车指数、穿衣指数、感冒指数、运动指数、旅游指数、紫外线指数、空气污染扩散条件指数、空调开启指数、过敏指数、太阳镜指数、化妆指数、晾晒指数、交通指数、钓鱼指数、防晒指数。

海外天气生活指数：运动指数、洗车指数、紫外线指数、钓鱼指数。

**接口地址**: `/v7/indices/{days}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| days | string | 是 | 预报天数（路径参数）。可选值：1d（1天）、3d（3天） |
| location | string | 是 | 需要查询地区的LocationID或经度,纬度坐标 |
| type | string | 是 | 生活指数的类型ID，可一次性获取多个类型，用英文逗号分割。例如 type=3,5 |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/indices/1d?type=1,2&location=101010100'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| daily[].date | string | 预报日期 |
| daily[].type | string | 生活指数类型ID |
| daily[].name | string | 生活指数类型的名称 |
| daily[].level | string | 生活指数预报等级 |
| daily[].category | string | 生活指数预报级别名称 |
| daily[].text | string | 生活指数预报的详细描述，可能为空 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "updateTime": "2021-12-16T18:35+08:00",
  "fxLink": "http://hfx.link/2ax2",
  "daily": [
    {
      "date": "2021-12-16",
      "type": "1",
      "name": "运动指数",
      "level": "3",
      "category": "较不宜",
      "text": "天气较好，但考虑天气寒冷，风力较强，推荐您进行室内运动，若户外运动请注意保暖并做好准备活动。"
    },
    {
      "date": "2021-12-16",
      "type": "2",
      "name": "洗车指数",
      "level": "3",
      "category": "较不宜",
      "text": "较不宜洗车，未来一天无雨，风力较大，如果执意擦洗汽车，要做好蒙上污垢的心理准备。"
    }
  ],
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

## 空气质量

全球空气质量API，适配当地空气质量标准，可以轻松的获取指定位置的空气质量、污染物和健康建议。

### 实时空气质量

**接口地址**: `/airquality/v1/current/{latitude}/{longitude}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| latitude | float | 是 | 所需位置的纬度（路径参数），最多支持小数点后两位 |
| longitude | float | 是 | 所需位置的经度（路径参数），最多支持小数点后两位 |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/airquality/v1/current/39.90/116.40'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| metadata.tag | string | 数据标签 |
| indexes[].code | string | 空气质量指数Code |
| indexes[].name | string | 空气质量指数的名字 |
| indexes[].aqi | float | 空气质量指数的值 |
| indexes[].aqiDisplay | string | 空气质量指数的值的文本显示 |
| indexes[].level | string | 空气质量指数等级，可能为空 |
| indexes[].category | string | 空气质量指数类别，可能为空 |
| indexes[].color.red/green/blue/alpha | int/float | 空气质量指数颜色（RGBA） |
| indexes[].primaryPollutant.code | string | 首要污染物的Code，可能为空 |
| indexes[].primaryPollutant.name | string | 首要污染物的名字，可能为空 |
| indexes[].primaryPollutant.fullName | string | 首要污染物的全称，可能为空 |
| indexes[].health.effect | string | 空气质量对健康的影响，可能为空 |
| indexes[].health.advice.generalPopulation | string | 对一般人群的健康指导意见 |
| indexes[].health.advice.sensitivePopulation | string | 对敏感人群的健康指导意见 |
| pollutants[].code | string | 污染物的Code |
| pollutants[].name | string | 污染物的名字 |
| pollutants[].fullName | string | 污染物的全称 |
| pollutants[].concentration.value | float | 污染物的浓度值 |
| pollutants[].concentration.unit | string | 污染物的浓度值单位 |
| pollutants[].subIndexes[].code | string | 污染物分指数的Code |
| pollutants[].subIndexes[].aqi | float | 污染物分指数的数值 |
| pollutants[].subIndexes[].aqiDisplay | string | 污染物分指数数值的显示名称 |
| stations[].id | string | AQI相关联的监测站Location ID |
| stations[].name | string | AQI相关联的监测站名称 |

**响应示例**:

```json
{
  "metadata": { "tag": "d75a323239766b831889e8020cba5aca9b90fca5080a1175c3487fd8acb06e84" },
  "indexes": [
    {
      "code": "us-epa",
      "name": "AQI (US)",
      "aqi": 46,
      "aqiDisplay": "46",
      "level": "1",
      "category": "Good",
      "color": { "red": 0, "green": 228, "blue": 0, "alpha": 1 },
      "primaryPollutant": { "code": "pm2p5", "name": "PM 2.5", "fullName": "Fine particulate matter (<2.5µm)" },
      "health": {
        "effect": "No health effects.",
        "advice": {
          "generalPopulation": "Everyone can continue their outdoor activities normally.",
          "sensitivePopulation": "Everyone can continue their outdoor activities normally."
        }
      }
    }
  ],
  "pollutants": [
    {
      "code": "pm2p5",
      "name": "PM 2.5",
      "fullName": "Fine particulate matter (<2.5µm)",
      "concentration": { "value": 11.0, "unit": "μg/m3" },
      "subIndexes": [ { "code": "us-epa", "aqi": 46, "aqiDisplay": "46" } ]
    }
  ],
  "stations": [
    { "id": "P51762", "name": "North Holywood" }
  ]
}
```

---

### 空气质量小时预报

**接口地址**: `/airquality/v1/hourly/{latitude}/{longitude}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| latitude | float | 是 | 所需位置的纬度（路径参数） |
| longitude | float | 是 | 所需位置的经度（路径参数） |
| localTime | bool | 否 | 是否返回本地时间。true=本地时间，false=UTC时间（默认） |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/airquality/v1/hourly/39.90/116.40'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| metadata.tag | string | 数据标签 |
| hours[].forecastTime | string | 预报时间 |
| hours[].indexes[].code | string | 空气质量指数Code |
| hours[].indexes[].name | string | 空气质量指数的名字 |
| hours[].indexes[].aqi | float | 空气质量指数的值 |
| hours[].indexes[].aqiDisplay | string | AQI值的文本显示 |
| hours[].indexes[].level | string | 等级，可能为空 |
| hours[].indexes[].category | string | 类别，可能为空 |
| hours[].indexes[].color | object | 空气质量指数颜色（RGBA） |
| hours[].indexes[].primaryPollutant | object | 首要污染物 |
| hours[].indexes[].health | object | 健康影响和建议 |
| hours[].pollutants[].code | string | 污染物Code |
| hours[].pollutants[].name | string | 污染物名字 |
| hours[].pollutants[].fullName | string | 污染物全称 |
| hours[].pollutants[].concentration.value | float | 浓度值 |
| hours[].pollutants[].concentration.unit | string | 浓度值单位 |
| hours[].pollutants[].subIndexes | array | 分指数 |

---

### 空气质量每日预报

**接口地址**: `/airquality/v1/daily/{latitude}/{longitude}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| latitude | float | 是 | 所需位置的纬度（路径参数） |
| longitude | float | 是 | 所需位置的经度（路径参数） |
| localTime | bool | 否 | 是否返回本地时间。true=本地时间，false=UTC时间（默认） |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/airquality/v1/daily/39.90/116.40'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| metadata.tag | string | 数据标签 |
| days[].forecastStartTime | string | 预报数据的开始时间，ISO8601格式 |
| days[].forecastEndTime | string | 预报数据的结束时间，ISO8601格式 |
| days[].indexes[].code | string | 空气质量指数Code |
| days[].indexes[].name | string | 空气质量指数的名字 |
| days[].indexes[].aqi | float | 空气质量指数的值 |
| days[].indexes[].aqiDisplay | string | AQI值的文本显示 |
| days[].indexes[].level | string | 等级，可能为空 |
| days[].indexes[].category | string | 类别，可能为空 |
| days[].indexes[].color | object | RGBA颜色值 |
| days[].indexes[].primaryPollutant | object | 首要污染物 |
| days[].indexes[].health | object | 健康影响和建议 |
| days[].pollutants[].code | string | 污染物Code |
| days[].pollutants[].name | string | 污染物名字 |
| days[].pollutants[].fullName | string | 污染物全称 |
| days[].pollutants[].concentration.value | float | 浓度值 |
| days[].pollutants[].concentration.unit | string | 浓度值单位 |
| days[].pollutants[].subIndexes | array | 分指数 |

---

### 监测站数据

**接口地址**: `/airquality/v1/station/{LocationID}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| LocationID | string | 是 | 空气质量监测站的LocationID（路径参数），可通过GeoAPI获取 |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/airquality/v1/station/P53763'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| metadata.tag | string | 数据标签 |
| metadata.sources | array | 数据来源或声明 |
| pollutants[].code | string | 污染物的Code |
| pollutants[].name | string | 污染物的名字 |
| pollutants[].fullName | string | 污染物的全称 |
| pollutants[].concentration.value | float | 污染物的浓度值 |
| pollutants[].concentration.unit | string | 污染物的浓度值的单位 |

---

## 时光机

时光机可以获取最近10天的历史天气和空气质量数据。

### 天气时光机

**接口地址**: `/v7/historical/weather`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | 需要查询的地区，仅支持LocationID |
| date | string | 是 | 选择日期，最多可选择最近10天（不包含今天）。格式：yyyyMMdd |
| lang | string | 否 | 多语言设置 |
| unit | string | 否 | 数据单位设置，可选值：m（公制，默认）、i（英制） |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/historical/weather?location=101010100&date=20200725'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| fxLink | string | 响应式页面链接 |
| weatherDaily.date | string | 当天日期 |
| weatherDaily.sunrise | string | 当天日出时间 |
| weatherDaily.sunset | string | 当天日落时间 |
| weatherDaily.moonrise | string | 当天月升时间 |
| weatherDaily.moonset | string | 当天月落时间 |
| weatherDaily.moonPhase | string | 当天月相名称 |
| weatherDaily.tempMax | string | 当天最高温度 |
| weatherDaily.tempMin | string | 当天最低温度 |
| weatherDaily.precip | string | 当天总降水量，默认单位：毫米 |
| weatherDaily.pressure | string | 大气压强，默认单位：百帕 |
| weatherDaily.humidity | string | 当天相对湿度，百分比 |
| weatherHourly[].time | string | 当天时间 |
| weatherHourly[].temp | string | 每小时温度 |
| weatherHourly[].icon | string | 天气状况图标代码 |
| weatherHourly[].text | string | 天气状况文字描述 |
| weatherHourly[].wind360 | string | 风向360角度 |
| weatherHourly[].windDir | string | 风向 |
| weatherHourly[].windScale | string | 风力等级 |
| weatherHourly[].windSpeed | string | 风速，公里/小时 |
| weatherHourly[].humidity | string | 每小时相对湿度 |
| weatherHourly[].precip | string | 每小时累计降水量 |
| weatherHourly[].pressure | string | 大气压强 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

---

### 空气质量时光机

**接口地址**: `/v7/historical/air`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | 需要查询的地区，仅支持LocationID |
| date | string | 是 | 选择日期，最多最近10天。格式：yyyyMMdd |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/historical/air?location=101010100&date=20200725'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| fxLink | string | 响应式页面链接 |
| airHourly[].pubTime | string | 空气质量数据发布时间 |
| airHourly[].aqi | string | 空气质量指数 |
| airHourly[].level | string | 空气质量指数等级 |
| airHourly[].category | string | 空气质量指数级别 |
| airHourly[].primary | string | 主要污染物，优时返回NA |
| airHourly[].pm10 | string | PM10 |
| airHourly[].pm2p5 | string | PM2.5 |
| airHourly[].no2 | string | 二氧化氮 |
| airHourly[].so2 | string | 二氧化硫 |
| airHourly[].co | string | 一氧化碳 |
| airHourly[].o3 | string | 臭氧 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

---

## 热带气旋（台风）

热带气旋（台风）API提供全球主要海洋流域的台风信息，包括台风实时位置、等级、气压、风速，还可查询台风路径和台风预报信息。

### 台风预报

**接口地址**: `/v7/tropical/storm-forecast`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stormid | string | 是 | 需要查询的台风ID，可通过台风列表API获取 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/tropical/storm-forecast?stormid=NP_2106'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| forecast[].fxTime | string | 台风预报时间 |
| forecast[].lat | string | 台风所处纬度 |
| forecast[].lon | string | 台风所处经度 |
| forecast[].type | string | 台风类型（TD/TS/STS/TY/STY/SuperTY） |
| forecast[].pressure | string | 台风中心气压 |
| forecast[].windSpeed | string | 台风附近最大风速 |
| forecast[].moveSpeed | string | 台风移动速度 |
| forecast[].moveDir | string | 台风移动方位 |
| forecast[].move360 | string | 台风移动方位360度方向 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**台风等级表** (GBT 19201-2006):

| 等级 | 最大平均风速(m/s) | 风力(级) |
|------|-------------------|----------|
| 热带气压（TD） | 10.8-17.1 | 6-7 |
| 热带风暴（TS） | 17.2-24.4 | 8-9 |
| 强热带风暴（STS） | 24.5-32.6 | 10-11 |
| 台风（TY） | 32.7-41.4 | 12-13 |
| 强台风（STY） | 41.5-50.9 | 14-15 |
| 超强台风（SuperTY） | ≥51.0 | 16或以上 |

---

### 台风实况和路径

**接口地址**: `/v7/tropical/storm-track`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stormid | string | 是 | 需要查询的台风ID，可通过台风列表API获取 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/tropical/storm-track?stormid=NP_2021'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| isActive | string | 是否为活跃台风。1=活跃，0=停编 |
| now.pubTime | string | 台风信息发布时间 |
| now.lat | string | 台风所处纬度 |
| now.lon | string | 台风所处经度 |
| now.type | string | 台风类型 |
| now.pressure | string | 台风中心气压 |
| now.windSpeed | string | 台风附近最大风速 |
| now.moveSpeed | string | 台风移动速度 |
| now.moveDir | string | 台风移动方位 |
| now.move360 | string | 台风移动方位360度方向 |
| now.windRadius30 | object | 台风7级风圈半径（东北/东南/西南/西北） |
| now.windRadius50 | object | 台风10级风圈半径 |
| now.windRadius64 | object | 台风12级风圈半径 |
| track[].time | string | 轨迹点时间 |
| track[].lat | string | 轨迹点纬度 |
| track[].lon | string | 轨迹点经度 |
| track[].type | string | 轨迹点台风类型 |
| track[].pressure | string | 轨迹点台风中心气压 |
| track[].windSpeed | string | 轨迹点风速 |
| track[].moveSpeed | string | 轨迹点移动速度 |
| track[].moveDir | string | 轨迹点移动方位 |
| track[].move360 | string | 轨迹点移动方位360度 |
| track[].windRadius30/50/64 | object | 轨迹点风圈半径 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

---

### 台风列表

**接口地址**: `/v7/tropical/storm-list`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| basin | string | 是 | 台风所在流域。当前仅支持NP（西北太平洋） |
| year | string | 是 | 查询年份，支持本年度和上一年度 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/tropical/storm-list?basin=NP&year=2020'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| storm[].id | string | 台风ID |
| storm[].name | string | 台风名称 |
| storm[].basin | string | 台风所处流域 |
| storm[].year | string | 台风所处年份 |
| storm[].isActive | string | 是否为活跃台风。1=活跃，0=停编 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

---

## 海洋数据

### 潮汐

未来10天全球潮汐数据，包括满潮、干潮高度和时间，逐小时潮汐数据。

**接口地址**: `/v7/ocean/tide`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | 潮汐站点的LocationID，可通过POI搜索服务（type=TSTA）获取 |
| date | string | 是 | 选择日期，最多未来10天（包含今天）。格式：yyyyMMdd |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/ocean/tide?location=P2951&date=20210206'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| tideTable[].fxTime | string | 满潮或干潮时间 |
| tideTable[].height | string | 海水高度，单位：米 |
| tideTable[].type | string | 满潮（H）或干潮（L） |
| tideHourly[].fxTime | string | 逐小时预报时间 |
| tideHourly[].height | string | 海水高度，单位：米 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

---

## 太阳辐射

### 太阳辐射预报

获取全球任意坐标的逐15分钟太阳辐射预报及相关数据，最多支持未来60小时预报，分辨率为1x1公里。

**接口地址**: `/solarradiation/v1/forecast/{latitude}/{longitude}`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| latitude | float | 是 | 所需位置的纬度（路径参数），最多支持小数点后两位 |
| longitude | float | 是 | 所需位置的经度（路径参数），最多支持小数点后两位 |
| hours | int | 否 | 预报小时数，可选1-60，默认24 |
| interval | int | 否 | 预报数据时间间隔，可选15、30、60分钟，默认60 |
| tilt | int | 否 | 光伏系统倾斜角度（0-90），当extra=poa时必传 |
| azimuth | int | 否 | 光伏系统方位角（0-359），0=北，当extra=poa时必传 |
| extra | string | 否 | 额外信息，可选weather（基本天气数据）、poa（阵列平面辐照度），多个用逗号分割 |
| localTime | bool | 否 | 是否返回本地时间。true=本地时间，false=UTC时间（默认） |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/solarradiation/v1/forecast/50.11/8.68'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| metadata.tag | string | 数据标签 |
| forecasts[].forecastTime | string | 预报时间，ISO8601格式 |
| forecasts[].solarAngle.azimuth | float | 太阳方位角，正北为0度，顺时针增加 |
| forecasts[].solarAngle.elevation | float | 太阳高度角 |
| forecasts[].dni.value | float | 法向直接辐照值，W/m² |
| forecasts[].dhi.value | float | 散射水平面辐照值，W/m² |
| forecasts[].ghi.value | float | 总水平面辐照值，W/m² |
| forecasts[].weather.temperature | object | 温度值及单位 |
| forecasts[].weather.windSpeed | object | 风速值及单位 |
| forecasts[].weather.humidity | int | 相对湿度，百分比 |
| forecasts[].poa.global | object | 组件平面总辐照值及单位 |
| forecasts[].poa.direct | object | 组件平面直接辐照量及单位 |
| forecasts[].poa.diffuse | object | 组件平面散射辐照量及单位 |
| forecasts[].poa.reflected | object | 组件平面地面反射辐照量及单位 |

**响应示例**:

```json
{
  "metadata": { "tag": "c4ca4238a0b923820dcc509a6f75849b" },
  "forecasts": [
    {
      "forecastTime": "2023-10-15T11:30Z",
      "solarAngle": { "azimuth": 184, "elevation": 40 },
      "dni": { "value": 25.16, "unit": "W/m²" },
      "dhi": { "value": 136.29, "unit": "W/m²" },
      "ghi": { "value": 152.57, "unit": "W/m²" },
      "weather": {
        "temperature": { "value": 18.6, "unit": "°C" },
        "windSpeed": { "value": 2.78, "unit": "m/s" },
        "humidity": 76
      },
      "poa": {
        "global": { "value": 134.39, "unit": "W/m²" },
        "direct": { "value": 9.35, "unit": "W/m²" },
        "diffuse": { "value": 125.04, "unit": "W/m²" },
        "reflected": { "value": 1.52, "unit": "W/m²" }
      }
    }
  ]
}
```

---

## 天文

### 日出日落

获取未来60天全球任意地点日出日落时间。

**接口地址**: `/v7/astronomy/sun`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | LocationID或经度,纬度坐标 |
| date | string | 是 | 选择日期，最多未来60天（包含今天）。格式：yyyyMMdd |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/astronomy/sun?location=101010100&date=20210220'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| sunrise | string | 日出时间，高纬度地区可能为空 |
| sunset | string | 日落时间，高纬度地区可能为空 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "updateTime": "2021-02-17T11:00+08:00",
  "fxLink": "http://hfx.link/2ax1",
  "sunrise": "2021-02-20T06:58+08:00",
  "sunset": "2021-02-20T17:57+08:00",
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

### 月升月落和月相

获取未来60天全球城市月升月落和逐小时的月相数据。

**接口地址**: `/v7/astronomy/moon`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | LocationID或经度,纬度坐标 |
| date | string | 是 | 选择日期，最多未来60天（包含今天）。格式：yyyyMMdd |
| lang | string | 否 | 多语言设置 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/astronomy/moon?location=101010100&date=20211120'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| updateTime | string | API的最近更新时间 |
| fxLink | string | 响应式页面链接 |
| moonrise | string | 当天月升时间，可能为空 |
| moonset | string | 当天月落时间，可能为空 |
| moonPhase[].fxTime | string | 月相逐小时预报时间 |
| moonPhase[].value | string | 月相数值 |
| moonPhase[].name | string | 月相名称 |
| moonPhase[].icon | string | 月相图标代码 |
| moonPhase[].illumination | string | 月亮照明度，百分比数值 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "updateTime": "2021-11-15T17:00+08:00",
  "fxLink": "http://hfx.link/2ax1",
  "moonrise": "2021-11-20T17:25+08:00",
  "moonset": "2021-11-21T07:42+08:00",
  "moonPhase": [
    {
      "fxTime": "2021-11-20T00:00+08:00",
      "value": "0.51",
      "name": "亏凸月",
      "illumination": "100",
      "icon": "805"
    }
  ],
  "refer": {
    "sources": ["QWeather"],
    "license": ["QWeather Developers License"]
  }
}
```

---

### 太阳高度角

任意时间点的全球太阳高度及方位角。

**接口地址**: `/v7/astronomy/solar-elevation-angle`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | 是 | 经度,纬度坐标（十进制，最多支持小数点后两位） |
| date | string | 是 | 查询日期，格式：yyyyMMdd |
| time | string | 是 | 查询时间，24时制，格式：HHmm |
| tz | string | 是 | 查询地区所在时区，例如 tz=0800 或 tz=-0530 |
| alt | string | 是 | 海拔高度，单位：米 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/v7/astronomy/solar-elevation-angle?location=120.34,36.08&alt=43&date=20210220&time=1230&tz=0800'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 状态码 |
| solarElevationAngle | string | 太阳高度角 |
| solarAzimuthAngle | string | 太阳方位角，正北顺时针方向角度 |
| solarHour | string | 太阳时，HHmm格式 |
| hourAngle | string | 时角 |
| refer.sources | array | 原始数据来源 |
| refer.license | array | 数据许可或版权声明 |

**响应示例**:

```json
{
  "code": "200",
  "solarElevationAngle": "42.88",
  "solarAzimuthAngle": "185.92",
  "solarHour": "1217",
  "hourAngle": "-4.41",
  "refer": {
    "sources": ["qweather.com"],
    "license": ["QWeather Developers License"]
  }
}
```

---

## 控制台API

帐号所有者可以为指定凭据开启控制台API权限，以便轻松的在本地访问控制台数据，了解当前财务和请求量统计。

**启用控制台API**:
默认情况下，所有凭据均没有权限请求控制台API，必须在凭据设置中启用控制台API才可以请求对应的数据。

### 财务汇总

查询你的财务和计费的汇总信息。

**接口地址**: `/finance/v1/summary`

**请求方法**: GET

**请求参数**: 无需参数。

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/finance/v1/summary'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| metadata.tag | string | 数据标签 |
| asOf | string | 当前数据的截止日期 |
| currency | string | 货币代码（CNY或USD） |
| balance | float | 可用额度 |
| accruedCharges.previousDay | float | 前一天应计费用总额 |
| accruedCharges.thisMonth | float | 本月应计费用总额 |
| accruedCharges.sinceLastBill | float | 从上次出账以来应计费用总额 |
| pendingBills[].number | string | 待支付账单号 |
| pendingBills[].date | string | 账单日期 |
| pendingBills[].type | string | 账单类型 |
| pendingBills[].status | string | 账单状态 |
| pendingBills[].amount | float | 账单总金额 |
| pendingBills[].amountDue | float | 账单剩余应付金额 |
| pendingBills[].dueDate | string | 应付日期 |
| availableSavingsPlans | array | 生效中或待生效的节省计划 |
| availableResourcePlans | array | 生效中或待生效的资源包 |

---

### 请求量统计

查询最近24小时的API请求量统计。

**接口地址**: `/metrics/v1/stats`

**请求方法**: GET

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| project | string | 否 | 指定项目ID以查看该项目请求量统计。与credential互斥 |
| credential | string | 否 | 指定凭据ID以查看该凭据请求量统计。与project互斥 |

**请求示例**:

```bash
curl -X GET --compressed \
-H 'Authorization: Bearer your_token' \
'https://your_api_host/metrics/v1/stats'
```

**响应参数**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| metadata.tag | string | 数据标签 |
| asOf | string | 当前数据的截止日期 |
| success[].api | string | 成功请求的API名称 |
| success[].hours | array | 最近24小时每小时的成功请求量 |
| errors[].api | string | 错误请求的API名称 |
| errors[].hours | array | 最近24小时每小时的错误请求量 |

**API名称对照表**:

| Code | 描述 |
|------|------|
| Geo | 地理信息 |
| Weather | 天气 |
| MinutelyForecast | 分钟降水预报 |
| WeatherIndices | 天气指数 |
| WeatherAlert | 天气预警 |
| AirQuality | 空气质量 |
| TimeMachine | 时光机 |
| Storm | 热带气旋（台风） |
| Astronomy | 天文 |
| SolarIrradiation | 太阳辐照 |
| Ocean | 海洋 |
| Console | 控制台API |

---

> 文档生成完毕。本文档覆盖了和风天气开放平台的全部12个API类别，共计29个API接口。
