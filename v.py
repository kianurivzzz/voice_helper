import pyttsx3

engn = pyttsx3.init()
engn.setProperty('rate', 180) #speech rate

#voice acting
def speaker(text):
    engn.say(text)
    engn.runAndWait()


#greeting
def speak(what):
    print(what)
    engn.say(what)
    engn.runAndWait()
    engn.stop()