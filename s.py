import os, sys, requests, subprocess, webbrowser, pyttsx3, datetime

engn = pyttsx3.init()
engn.setProperty('rate', 180) #speech rate


def speak(what):
    print(what)
    engn.say( what )
    engn.runAndWait()
    engn.stop()

#says text
def speaker(text):
    engn.say(text)
    engn.runAndWait()
    

#says greeting
#def salute():


#check weather
#def weather():


#open browser
def browser():
    webbrowser.open('https://www.google.ru/', new = 2)
    
    
def watchfilm():
    webbrowser.open('https://clck.ru/saBzY', new = 2)
    
    
def watchYT():
    webbrowser.open('https://www.youtube.com/', new = 2)


def nowtime():
    now = datetime.datetime.now()
    speak(str(now.hour) + ":" + str(now.minute))
    
#open game
def game():
    subprocess.Popen('C:\Games\Saints Row The Third\SaintsRowTheThird.exe')
    
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
