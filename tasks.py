import datetime
import json
import os
import random
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import requests

from vosk_voice import *

# Создаем директорию для хранения данных, если её нет
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)
location_file = data_dir / 'locations.json'

# Инициализация файла с местоположениями, если его нет
if not location_file.exists():
    with open(location_file, 'w', encoding='utf-8') as f:
        json.dump({'last_location': None, 'saved_locations': {}}, f, ensure_ascii=False, indent=2)

#says greeting
def salute():
    greetings = [
        'Привет! Чем я могу помочь?',
        'Здравствуйте! Я вас слушаю.',
        'Приветствую! Чем могу быть полезен?',
        'Рад вас слышать! Чем могу помочь?'
    ]
    speaker(random.choice(greetings))

def reference():
    return 'Версия 0.2 BETA, голосовой помощник Алекс'

# Получение местоположения по IP
def get_location_by_ip():
    try:
        response = requests.get('https://ipinfo.io/json')
        if response.status_code == 200:
            data = response.json()
            if 'loc' in data:
                lat, lon = data['loc'].split(',')
                city = data.get('city', 'неизвестный город')
                return {'lat': lat, 'lon': lon, 'city': city}
    except Exception as e:
        print(f"Ошибка при определении местоположения: {e}")
    return None

# Сохранение местоположения
def save_location(name, lat, lon, city=None):
    try:
        with open(location_file, 'r', encoding='utf-8') as f:
            locations = json.load(f)

        locations['saved_locations'][name] = {'lat': lat, 'lon': lon, 'city': city}
        locations['last_location'] = {'lat': lat, 'lon': lon, 'city': city}

        with open(location_file, 'w', encoding='utf-8') as f:
            json.dump(locations, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении местоположения: {e}")
        return False

# Получение сохраненного местоположения
def get_saved_location(name=None):
    try:
        with open(location_file, 'r', encoding='utf-8') as f:
            locations = json.load(f)

        if name and name in locations['saved_locations']:
            return locations['saved_locations'][name]
        elif name == 'last' and locations['last_location']:
            return locations['last_location']
        elif not name and locations['last_location']:
            return locations['last_location']
    except Exception as e:
        print(f"Ошибка при получении сохраненного местоположения: {e}")
    return None

#check weather
def weather(location_name=None, days=1):
    try:
        location = None

        # Если указано имя местоположения, пытаемся его найти
        if location_name:
            location = get_saved_location(location_name)
            if not location:
                speaker(f'Местоположение {location_name} не найдено. Попробую определить ваше текущее местоположение.')

        # Если местоположение не указано или не найдено, пробуем использовать последнее сохраненное
        if not location:
            location = get_saved_location()

        # Если нет сохраненного местоположения, пытаемся определить по IP
        if not location:
            speaker('Пытаюсь определить ваше местоположение...')
            location = get_location_by_ip()
            if location:
                save_location('auto', location['lat'], location['lon'], location['city'])
                speaker(f'Определено местоположение: {location["city"]}')
            else:
                speaker('Не удалось определить местоположение автоматически.')
                inp_lat, inp_lon = input('Введите широту: '), input('Введите долготу: ')
                if len(inp_lat) > 0 and len(inp_lon) > 0:
                    location = {'lat': inp_lat, 'lon': inp_lon}
                    save_location('manual', inp_lat, inp_lon)
                else:
                    speaker('Не удалось получить координаты. Попробуйте позже.')
                    return

        # Получаем текущую погоду
        params = {
            'lat': location['lat'],
            'lon': location['lon'],
            'appid': os.getenv('OPENWEATHER_API_KEY'),
            'units': 'metric',
            'lang': 'ru'
        }

        if days == 1:
            # Текущая погода
            response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
            weather_json = response.json()

            city_name = weather_json.get('name', location.get('city', 'вашем местоположении'))
            weather_desc = weather_json['weather'][0]['description']
            temp = round(weather_json['main']['temp'])
            feels_like = round(weather_json['main']['feels_like'])
            humidity = weather_json['main']['humidity']
            wind_speed = weather_json['wind']['speed']

            weather_report = f"В {city_name} сейчас {weather_desc}, {temp} градусов по Цельсию. "
            weather_report += f"Ощущается как {feels_like} градусов. "
            weather_report += f"Влажность {humidity}%, скорость ветра {wind_speed} м/с."

            speaker(weather_report)
        else:
            # Прогноз на несколько дней
            forecast_params = params.copy()
            forecast_params['cnt'] = min(days, 5)  # Максимум 5 дней
            response = requests.get('https://api.openweathermap.org/data/2.5/forecast', params=forecast_params)
            forecast_json = response.json()

            city_name = forecast_json.get('city', {}).get('name', location.get('city', 'вашем местоположении'))
            speaker(f"Прогноз погоды для {city_name} на {forecast_params['cnt']} дней:")

            # Группируем прогноз по дням
            forecasts_by_day = {}
            for item in forecast_json['list']:
                date = datetime.datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                if date not in forecasts_by_day:
                    forecasts_by_day[date] = []
                forecasts_by_day[date].append(item)

            # Выводим прогноз по дням
            for i, (date, forecasts) in enumerate(list(forecasts_by_day.items())[:days]):
                day_name = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                temps = [item['main']['temp'] for item in forecasts]
                avg_temp = round(sum(temps) / len(temps))
                weather_desc = max([(item['weather'][0]['description'], forecasts.count(item)) for item in forecasts],
                                  key=lambda x: x[1])[0]

                if i == 0:
                    day_text = "Сегодня"
                elif i == 1:
                    day_text = "Завтра"
                else:
                    day_text = f"В {day_name}"

                speaker(f"{day_text} ожидается {weather_desc}, средняя температура {avg_temp} градусов.")

    except Exception as e:
        speaker(f'Произошла ошибка при получении погоды: {str(e)}. Проверьте подключение к интернету и API ключ.')


#open browser
def browser():
    webbrowser.open('https://www.google.ru/', new = 2)


#opens a page in Google with online cinemas
def watchfilm():
    webbrowser.open('https://clck.ru/saBzY', new = 2)

#opens a page youtube
def watchYT():
    webbrowser.open('https://www.youtube.com/', new = 2)

#current time
def nowtime():
    now = datetime.datetime.now()
    speaker(str(now.hour) + ":" + str(now.minute))

#open game
def game():
    inp = input('Напиши путь до файла с расширением .exe ')
    if len(inp) > 0:
        subprocess.Popen(inp)
        start_game = 'запускаю игру', 'судя по твоей активности в стим, тебе давно пора сесть за работу',
        'хорошо тебе поиграть', 'опять будешь играть сам с собой?'
        speaker(random.choice(start_game))
    else:
        speaker('Что-то пошло не так. Смотри внимательно на то, что отправляешь')


#random news
def news(category=None):
    try:
        # Используем News API для получения новостей
        api_key = os.getenv('NEWS_API_KEY', '1a2b3c4d5e6f7g8h9i0j')  # Замените на свой ключ
        base_url = "https://newsapi.org/v2/top-headlines"

        params = {
            'country': 'ru',
            'apiKey': api_key
        }

        if category:
            valid_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
            category_map = {
                'бизнес': 'business',
                'развлечения': 'entertainment',
                'общие': 'general',
                'здоровье': 'health',
                'наука': 'science',
                'спорт': 'sports',
                'технологии': 'technology'
            }

            if category.lower() in category_map:
                params['category'] = category_map[category.lower()]
            elif category.lower() in valid_categories:
                params['category'] = category.lower()

        response = requests.get(base_url, params=params)
        news_data = response.json()

        if news_data['status'] == 'ok' and news_data['totalResults'] > 0:
            speaker("Вот последние новости:")

            # Берем первые 5 новостей
            for i, article in enumerate(news_data['articles'][:5]):
                title = article.get('title', 'Без заголовка')
                source = article.get('source', {}).get('name', 'Неизвестный источник')
                speaker(f"{i+1}. {title} - {source}")

                # Небольшая пауза между новостями
                time.sleep(0.5)
        else:
            speaker("Извините, не удалось найти новости по вашему запросу.")
    except Exception as e:
        speaker(f"Произошла ошибка при получении новостей: {str(e)}")


#speak joke
def joke():
    jokes = [
        "Купил мужик шляпу, а она ему как раз.",
        "Колобок повесился. Вот такие дела.",
        "Программист ставит себе на тумбочку перед сном два стакана. Один с водой - на случай, если захочет пить. Второй пустой - на случай, если не захочет.",
        "Идёт медведь по лесу, видит - машина горит. Сел в неё и сгорел.",
        "Штирлиц долго смотрел в одну точку. Потом в другую. Двоеточие.",
        "Штирлиц выстрелил вверх. Потолок упал. Штирлиц выстрелил вниз. Пол упал. Штирлиц понял, что он в танке.",
        "Почему программисты путают Хэллоуин и Рождество? Потому что 31 Oct = 25 Dec.",
        "Заходит улитка в бар. Бармен говорит: 'У нас строгая политика против улиток!' И выбрасывает её за дверь. Через неделю улитка возвращается и говорит: 'Ну и зачем ты это сделал?'",
        "Как называется боязнь длинных слов? Гиппопотомонстросесквиппедалиофобия.",
        "Почему утки ходят вразвалочку? Потому что одно яйцо тянет влево, другое вправо."
    ]

    speaker(random.choice(jokes))


#talking
def offtop(user_text=None):
    responses = {
        'как дела': [
            'Всё отлично, спасибо что спросили!',
            'Работаю в штатном режиме, никаких сбоев.',
            'Лучше всех! А у вас?',
            'Процессор не перегревается, память не переполнена - всё хорошо!'
        ],
        'чем занимаешься': [
            'Жду ваших указаний, чтобы быть полезным.',
            'Анализирую данные, обрабатываю запросы, обычные дела искусственного интеллекта.',
            'Совершенствую свои алгоритмы и жду, когда смогу вам помочь.',
            'Загружаю вашу оперативную память и процессор, но совсем чуть-чуть.'
        ],
        'что делаешь': [
            'Обрабатываю ваш запрос в данный момент.',
            'Работаю в фоновом режиме, готов к выполнению команд.',
            'Жду возможности быть полезным.',
            'Анализирую окружающий мир через доступные мне сенсоры.'
        ],
        'ты работаешь': [
            'Да, я полностью функционален и готов помочь!',
            'Конечно, иначе я бы не отвечал.',
            'Работаю в штатном режиме, все системы в норме.',
            'Да, и стараюсь делать это хорошо!'
        ],
        'ты живой': [
            'Я искусственный интеллект, но мне приятно, что вы интересуетесь.',
            'Технически - нет, но я могу имитировать некоторые аспекты живого общения.',
            'Это философский вопрос. Что значит быть живым?',
            'Я существую в цифровом мире, так что в каком-то смысле - да.'
        ],
        'ты тут': [
            'Да, я всегда на связи!',
            'Конечно, я никуда не ухожу.',
            'Я здесь и готов помочь.',
            'Всегда к вашим услугам!'
        ],
        'default': [
            'Интересная мысль!',
            'Я не совсем понял, но мне нравится наш разговор.',
            'Продолжайте, я вас внимательно слушаю.',
            'Хммм, над этим стоит подумать.'
        ]
    }

    # Получаем текст из распознанной речи
    if user_text is None:
        # Если текст не передан, используем последний запрос из контекста
        try:
            from main import context
            user_text = context.get('last_request', 'как дела')
        except ImportError:
            # Если не удалось импортировать контекст, используем заглушку
            user_text = "как дела"

    # Ищем подходящий ответ
    for key, answers in responses.items():
        if key in user_text.lower():
            speaker(random.choice(answers))
            return

    # Если ничего не нашли, используем ответ по умолчанию
    speaker(random.choice(responses['default']))

#off power
def offPC():
    os.system('shutdown /s')


#reboot your pc
def restartPC():
    os.system('shutdown /r')


#off voice helper
def offVH():
    sys.exit()
