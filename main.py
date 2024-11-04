# นำไลบารีเข้ามาใช้งาน
from dotenv import load_dotenv
from typing import Final
import os
import discord 
import requests
import aiohttp
from discord import app_commands, Embed
from discord.ext import commands

# โหลด API Key จาก .env เพื่อใช้งาน
load_dotenv()
token: Final[str] = os.getenv('token')
print(token)

# กำหนด intents เพื่อใช้งาน
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ฟังก์ชันสำหรับ  ดำะแ้ api คุณภาพอากาศ
async def fetch_air_quality(city_name: str) -> None:
    url = f"https://api.waqi.info/feed/{requests.utils.quote(city_name)}/?token={os.getenv('WAQI_API_TOKEN')}"
    try:
        response = requests.get(url)
        json_data = response.json()
        
        # หากข้อมูล api ที่ส่งมาเป็นไฟล์ json สถานะ ok
        if json_data['status'] == "ok":
            return json_data['data']
        else:
            print("เกิดข้อผิดพลาดในการดึงข้อมูล", json_data)
    except Exception as error:
        print("Fetch error:", error)


# ฟังก์ชั่นสำหรับ Fetch ข้อมูลสภาพอากาศ
async def fetch_weather(province, amphoe) -> None:
    url = f"https://data.tmd.go.th/nwpapi/v1/forecast/location/daily/place?province={requests.utils.quote(province)}&amphoe={requests.utils.quote(amphoe)}&fields=tc_max,rh&duration=2"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers={
                "accept": "application/json",
                "authorization": f"Bearer {os.getenv('TMD_API_TOKEN')}",
            }) as response:
                json_data = await response.json()

                if 'WeatherForecasts' in json_data and json_data['WeatherForecasts']:
                    return json_data['WeatherForecasts'][0]
                else:
                    print("เกิดข้อผิดพลาดในการดึงข้อมูล", json_data)   
        except Exception as error:
            print("Fetch error:", error)

# อีเว้ทน์หากบอทพร้อมใช้งาน
@bot.event
async def on_ready():
    print(f'✅ เข้อสู่ระบบ {bot.user} (ไอดี: {bot.user.id})')
    # ซิงค์คำสั่ง Slash command
    try:
        await bot.tree.sync()
        print("Slash commands have been synced!")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print('------')

# Slash command สำหรับเช็คคุณภาพอากสศ
@bot.tree.command(name="airquality", description="ตรวจสอบคุณภาพอากาศวันนี้")
@app_commands.describe(city="พิมพ์ชื่อเมืองที่คุณต้องการ")
async def airquality(interaction: discord.Interaction, city: str):
   data = await fetch_air_quality(city)
   if data:
        aqi = data['aqi']
        city_info = data['city']['name']
        dominant_pol = data['dominentpol'].upper()
        timestamp = data['time']['iso']
        
        general_info_embed = Embed(
            description=f"### 🌿 ข้อมูลคุณภาพอากาศของ **{city_info}**\n> ``🔎`` **ผลการค้นหา:** {city_info}\n> ``🔰`` **ดัชนีคุณภาพอากาศ (AQI):** {aqi}\n> ``🚬`` **สารมลพิษหลัก:** {dominant_pol}\n> ``⌛`` **เวลา:** {timestamp}",
            color=0x00FFFF
        )

        pollutant_info_embed = Embed(color=0x00FFFF)
        iaqi = data['iaqi']
        pollutant_info_embed.add_field(name="🍂 ฝุ่น PM 2.5", value=f"```{iaqi['pm25']['v']}```" if 'pm25' in iaqi and 'v' in iaqi['pm25'] else "N/A", inline=True)
        pollutant_info_embed.add_field(name="🌵 ฝุ่น PM 10", value=f"```{iaqi['pm10']['v']}```" if 'pm10' in iaqi and 'v' in iaqi['pm10'] else "N/A", inline=True)
        pollutant_info_embed.add_field(name="💧 โอโซน (O3)", value=f"```{iaqi['o3']['v']}```" if 'o3' in iaqi and 'v' in iaqi['o3'] else "N/A", inline=True)
        pollutant_info_embed.add_field(name="🍇 แก๊ส Nitrogen Dioxide (NO2)", value=f"```{iaqi['no2']['v']}```" if 'no2' in iaqi and 'v' in iaqi['no2'] else "N/A", inline=True)
        pollutant_info_embed.add_field(name="⛅ จุดน้ำค้าง", value=f"```{iaqi['dew']['v']}°C```" if 'dew' in iaqi and 'v' in iaqi['dew'] else "N/A", inline=True)
        pollutant_info_embed.add_field(name="💨 ซัลเฟอร์ไดออกไซด์ (SO2)", value=f"```{iaqi['so2']['v']}```" if 'so2' in iaqi and 'v' in iaqi['so2'] else "N/A", inline=True)
        pollutant_info_embed.add_field(name="🔺 อุณหภูมิ", value=f"```{iaqi['t']['v']} °C```" if 't' in iaqi and 'v' in iaqi['t'] else "N/A", inline=True)
        pollutant_info_embed.add_field(name="🍃 ความเร็วลม", value=f"```{iaqi['w']['v']} m/s```" if 'w' in iaqi and 'v' in iaqi['w'] else "N/A", inline=True)

        await interaction.response.send_message(embeds=[general_info_embed, pollutant_info_embed])
   else:
        await interaction.response.send_message("❌ ไม่สามารถดึงข้อมูลได้หรือมีบางอย่างผิดพลาด")


# Slash command สำหรับเช็คสภาพอากาศ
@bot.tree.command(name="weather", description="ดูข้อมูลสภาพอากาศ")
@app_commands.describe(province="ชื่อจังหวัด")
@app_commands.describe(amphoe="ชื่ออำเภอ")
async def weather(interaction: discord.Interaction, province: str, amphoe: str):
    await interaction.response.defer(thinking=True)
    data = await fetch_weather(province, amphoe)
    
    if data:
        location = data['location']
        forecasts = data['forecasts']

        weather_embed = Embed(
            title=f"🌤️ ข้อมูลสภาพอากาศจาก {location['amphoe']}, {location['province']}",
            color=0x0000FF
        )
        
        for forecast in forecasts:
            weather_embed.add_field(
                name=f"📅 วันที่: {forecast['time']}",
                value=f"🌡️ อุณหภูมิ: {forecast['data']['tc_max']} °C\n💧 ความชื้นในอากาศ: {forecast['data']['rh']}%",
                inline=True
            )

        await interaction.followup.send(embed=weather_embed)
    else:
        await interaction.followup.send("❌ ไม่สามารถดึงข้อมูลได้หรือมีบางอย่างผิดพลาด")


# เมื่อเริ่มใช้งานบอท
def main() -> None:
    bot.run(token=token)

if __name__ == '__main__':
    main()


