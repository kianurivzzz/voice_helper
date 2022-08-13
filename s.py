import os, sys, requests, subprocess, webbrowser, datetime
from config import API_TOKEN
from v import *
    
#says greeting
#def salute():


#check weather
def weather():
    try:
        params = {'lat' : 'your lat', 'lon' : 'your lon', 'appid' : API_TOKEN,
            'units' : 'metric', 'lang' : 'ru'
            }
        response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
        weather_json = response.json()
        speaker(f"За окном {weather_json['weather'][0]['description']} и {round(weather_json['main']['temp'])} градусов по Цельсию")
    except:
        speaker('Произошла ошибка при подключении к API. Проверьте его правильность.')
    


#open browser
def browser():
    webbrowser.open('https://www.google.ru/', new = 2)
    
    
def watchfilm():
    webbrowser.open('https://clck.ru/saBzY', new = 2)
    
    
def watchYT():
    webbrowser.open('https://www.youtube.com/', new = 2)


def nowtime():
    now = datetime.datetime.now()
    speaker(str(now.hour) + ":" + str(now.minute))
    
#open game
def game():
    subprocess.Popen('C:\Games\Saints Row The Third\SaintsRowTheThird.exe')
    
    
#random news
#def news():
        
    
#talking
def offtop():
    pass
    
#off power 
def offPC():
    os.system('shutdown /s')


def restartPC():
    os.system('shutdowm /r')


#off voice helper
def offVH():
    sys.exit()
