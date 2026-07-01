from bs4 import BeautifulSoup
import pandas as pd
import requests


city_codes = {
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280101",
    "深圳": "101280601",
    "杭州": "101210101"
}

def get_city_info(city_codes):
    while True:
        city_name = input("请输入城市名称（北京、上海、广州、深圳、杭州）：").strip()

        if city_name not in city_codes:
            print("暂时不支持这个城市,请重新输入")
        else:
            city_code = city_codes[city_name]
            return city_name, city_code
        
def build_weather_url(city_code):
    return f"https://www.weather.com.cn/weather/{city_code}.shtml"

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = response.apparent_encoding
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    return soup

def extract_weather_data(soup, city_name):
    days = soup.select("ul.t.clearfix li")
    weather_data = []

    for day in days:
        date = day.select_one("h1").text
        weather = day.select_one(".wea").text
        temperature = day.select_one(".tem").text.strip()
        wind = day.select_one(".win").text.strip()

        one_day = {
            "城市":city_name,
            "日期":date,
            "天气":weather,
            "温度":temperature,
            "风力":wind
        }
        weather_data.append(one_day)
        print(f"城市:{city_name},日期：{date},天气：{weather},温度：{temperature},风力：{wind}")
    return weather_data

def save_to_excel(weather_data, file_name):
    df = pd.DataFrame(weather_data)
    df.to_excel(file_name, index=False)
    print(f"保存成功:{file_name}")

def main():
    city_name, city_code = get_city_info(city_codes)

    url = build_weather_url(city_code)

    soup = get_soup(url)

    weather_data = extract_weather_data(soup, city_name)

    file_name = f"{city_name}_weather.xlsx"
    save_to_excel(weather_data, file_name)

if __name__ == "__main__":
    main()
# html = """
# <div class="weather-card">
#     <h1>北京</h1>
#     <p class="date">6月30日</p>
#     <p class="weather">多云</p>
#     <p class="temperature">28℃</p>
# </div>

# <div class="weather-card">
#     <h1>北京</h1>
#     <p class="date">7月1日</p>
#     <p class="weather">小雨</p>
#     <p class="temperature">25℃</p>
# </div>

# <div class="weather-card">
#     <h1>北京</h1>
#     <p class="date">7月2日</p>
#     <p class="weather">晴</p>
#     <p class="temperature">31℃</p>
# </div>
# """






# print(len(days))
# title = soup.select_one("h1").text
# desc = soup.select_one("p").text
# print(desc)
# print(title)

# cards = soup.select(".weather-card")


  
# # print (weather_data)
# for item in weather_data:
#     print(item["城市"], item["日期"], item["天气"], item["温度"])








    # print(city)                   前面使用的数据
    # print(date)
    # print(weather)
    # print(temperature)