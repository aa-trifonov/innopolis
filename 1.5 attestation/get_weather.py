import re
import asyncio
from aiohttp import ClientSession
import time


class Weather:
    def __init__(self, city, wtype, temp, max_temp, min_temp, wind, wspeed, gust):
        self.city = city                    # город
        self.wtype = wtype                  # тип погоды
        self.temp = temp                    # температура
        self.max_temp = max_temp            # макс. температура
        self.min_temp = min_temp            # мин. температура
        self.wind = wind                    # ветер
        self.wspeed = wspeed                # скорость ветра
        self.gust = gust                    # порывы ветра

    def return_weather(self):
        return f'{"-"*25} {self.city} {"-"*25}\n' \
               f'Сейчас {self.wtype}, температура воздуха {self.temp} градусов Цельсия.\n' \
               f'Минимальная температура в течение суток {self.min_temp}, максимальная {self.max_temp}.\n' \
               f'Ветер {wind_direction(self.wind)}, скорость {self.wspeed} м/с с порывами до {self.gust} м/с.\n'


# ф-я преобразования направления ветра из градусов в сторону света
def wind_direction(wind_deg):
    if 337.5 < wind_deg < 360 or 0 <= wind_deg <= 22.5:
        return 'северный'
    elif 22.5 < wind_deg <= 67.5:
        return 'северо-восточный'
    elif 67.5 < wind_deg <= 112.5:
        return 'восточный'
    elif 112.5 < wind_deg <= 157.5:
        return 'юго-восточный'
    elif 157.5 < wind_deg <= 202.5:
        return 'южный'
    elif 202.5 < wind_deg <= 247.5:
        return 'юго-западный'
    elif 247.5 < wind_deg <= 292.5:
        return 'западный'
    elif 292.5 < wind_deg <= 337.5:
        return 'северо-западный'


with open('cities.txt', 'r', encoding='utf-8') as file:
    info = file.read()
    pattern = r'.{3}(\w\D+) [-\d]'
    cities = []
    for s in re.findall(pattern, info):
        if '-' in s:
            cities.append(s[:-2])
        else:
            cities.append(s)


async def get_weather(city):
    async with ClientSession() as session:
        url = f'http://api.openweathermap.org/data/2.5/weather'
        params = {'q': city, 'APPID': '2a4ff86f9aaa70041ec8e82db64abf56', 'units': 'metric', 'lang': 'ru'}

        async with session.get(url=url, params=params) as response:
            weather_json = await response.json()
            if weather_json['cod'] == 200:  # возвращает json только если ответ с сервера получен
                return weather_json


async def main(cities_list):
    tasks = []
    for city in cities_list:  # формирование списка асинхронных задач
        tasks.append(asyncio.create_task(get_weather(city)))

    weather_cities = []
    for task in tasks:  # выполнение асинхронных задач
        wc = await task
        try:            # создание экземпляров класса Weather для каждого города
            weather_cities.append(Weather(wc['name'], wc['weather'][0]['description'],
                                          wc['main']['temp'], wc['main']['temp_max'],
                                          wc['main']['temp_min'], wc['wind']['deg'],
                                          wc['wind']['speed'], wc['wind']['gust']))
        except KeyError:  # в случае, если в ответе нет данных о порывах ветра
            weather_cities.append(Weather(wc['name'], wc['weather'][0]['description'],
                                          wc['main']['temp'], wc['main']['temp_max'],
                                          wc['main']['temp_min'], wc['wind']['deg'],
                                          wc['wind']['speed'], 0))

    print(f'Погода по {len(weather_cities)}/{len(cities)} городам получена.\n')
    return weather_cities


start_time = time.monotonic()
# запуск ф-и main
a = asyncio.run(main(cities))  # возвращает список объектов класса Weather
for j in range(len(cities)):
    print(a[j].return_weather())  # вызов метода класса Weather

print(f'Время выполнения программы {time.monotonic() - start_time} секунд.')
