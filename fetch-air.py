import requests
import os

async def fetch_air_quality(city_name: str) -> None:
    url = f"https://api.waqi.info/feed/{requests.utils.quote(city_name)}/?token={os.getenv('WAQI_API_TOKEN')}"
    try:
        response = requests.get(url)
        json_data = response.json()

        if json_data['status'] == "ok":
            return json_data['data']
        else:
            print("เกิดข้อผิดพลาดในการดึงข้อมูล", json_data)
    except Exception as error:
        print("Fetch error:", error)
