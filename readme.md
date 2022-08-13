# Описание голосового помощника Diana v0.1 ALPHA

Голосовой помощник в процессе разработки. Постепенно будут добавляться новые функции и будет обновляться база "обращение - ответ".

## Содержание:
1. [Функционал](https://github.com/kianurivzzz/diana_voice_helper#сейчас-она-умеет)
2. [Для запуска потребуется](https://github.com/kianurivzzz/diana_voice_helper#для-запуска-потребуется)
3. [Библиотеки](https://github.com/kianurivzzz/diana_voice_helper#библиотеки)
4. [Языковые пакеты](https://github.com/kianurivzzz/diana_voice_helper#языковые-пакеты-для-vosk)

### Сейчас она умеет: 
-Называть текущее время
-Общаться (немного)
-Открывать браузер
-Открывать игру
-Выключать и перезагружать компьютер
-Отключаться по команде
-Называть текущаю погоду в вашем городе. Для работоспобности этой функции: 
1. Вставьте ваш токен openweather 
    > файл config
2. Вставьте долготу и широту 
    > файл s 
        >>функция weather

### Для запуска потребуется: 

1. Python версии 3.8 и выше*
2. Набор библиотек
3. Языковой пакет

<font size = 3> *Программа тестировалась на Python 3.10.4 </font>

### Библиотеки:

[vosk PyPi](https://pypi.org/project/vosk/)

[vosk GitHub](https://github.com/alphacep/vosk-api)

[vosk](https://alphacephei.com/vosk/

[sounddevice](https://pypi.org/project/sounddevice/)

[pyttsx3](https://pypi.org/project/pyttsx3/)

[requests](https://pypi.org/project/requests/)

[sklearn PyPi](https://pypi.org/project/scikit-learn/)

[sklearn site](https://scikit-learn.org/stable/)

### Языковые пакеты для vosk:

Перед запуском обязательно скачайте и распакуйте языковой пакет в папку с программой.

[Полный языковой пакет vosk (вес 1.5Gb)](https://alphacephei.com/vosk/models/vosk-model-ru-0.22.zip)
[Упрощённый языковой пакет vosk (вес 40 Mb)](https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip)



