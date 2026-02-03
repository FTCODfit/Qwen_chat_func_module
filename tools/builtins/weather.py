from tools.decorator import tool
from tools.schema import ToolParameter
import requests

@tool(
    name="get_weather",
    description="当用户明确想查询地区天气时调用此工具",
    parameters={
        "city":ToolParameter(
            type="string",
            description="城市的简体中文名称，例如台北、新北、东京。"
        )
    },
    required=["city"]
)
def get_weather(city: str) -> dict:
    coords = _geocode_city(city)
    if not coords:
        return {"city": city, "error": "找不到查詢的城市"}

    lat, lon = coords
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }

    r = requests.get(url, params=params, timeout=3)
    r.raise_for_status()
    data = r.json()["current_weather"]
    
    WEATHER_CODE_MAP = {
                        0: "晴朗",
                        1: "大致晴朗",
                        2: "部分多雲",
                        3: "陰天",
                        45: "霧",
                        48: "霧凇",
                        51: "小毛毛雨",
                        61: "小雨",
                        80: "短暫陣雨"}
    
    return {
        "城市": city,
        "當地溫度": data["temperature"],
        "風速": data["windspeed"],
        "天氣狀況": WEATHER_CODE_MAP.get(data["weathercode"])
    }

from functools import lru_cache
@lru_cache(maxsize=128) # 加快取免得每次一直查
def _geocode_city(city: str) -> tuple[float, float] | None:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    r = requests.get(url, params=params, timeout=5)
    r.raise_for_status()
    data = r.json()

    results = data.get("results")
    if not results:
        return None

    return results[0]["latitude"], results[0]["longitude"]

