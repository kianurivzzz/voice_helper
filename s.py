import os, sys, requests, subprocess, webbrowser, datetime, random
from config import API_TOKEN
from v import *
    
#says greeting
#def salute():


def reference():
    return 'Версия 0.1 APLHA, голосовой помощник Диана'


#check weather
def weather():
    try:
        inp_lat, inp_lon = input('Введи широту '), input('Введи долготу ')
        if len(inp_lat) and len(inp_lon) > 0:
            params = {'lat' : inp_lat, 'lon' : inp_lon, 'appid' : API_TOKEN,
                'units' : 'metric', 'lang' : 'ru'
                }
            response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
            weather_json = response.json()
            speaker(f"За окном {weather_json['weather'][0]['description']} и {round(weather_json['main']['temp'])} градусов по Цельсию")
    except:
        speaker('Произошла ошибка при подключении к API. Проверь его правильность.')
    

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
#def news():
        

#speak joke
def joke():
    pass


#talking
def offtop():
    pass
    
#off power 
def offPC():
    os.system('shutdown /s')


#reboot your pc
def restartPC():
    os.system('shutdowm /r')


#off voice helper
def offVH():
    sys.exit()
