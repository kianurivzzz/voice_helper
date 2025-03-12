import logging
import threading
from pathlib import Path

import pyttsx3

# Создаем директорию для логов, если её нет
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'voice_helper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('voice')

# Инициализация движка синтеза речи
try:
    engn = pyttsx3.init()
    engn.setProperty('rate', 180)  # speech rate

    # Получение доступных голосов
    voices = engn.getProperty('voices')

    # Сначала попробуем найти мужской русский голос
    male_ru_voice_found = False
    for voice in voices:
        # Проверяем, что голос русский и мужской
        is_russian = 'russian' in voice.name.lower() or 'ru' in voice.id.lower()
        is_male = voice.gender == 'male' if hasattr(voice, 'gender') else ('male' in voice.name.lower())

        if is_russian and is_male:
            engn.setProperty('voice', voice.id)
            logger.info(f"Установлен мужской русский голос: {voice.name}")
            male_ru_voice_found = True
            break

    # Если мужской русский голос не найден, ищем любой русский
    if not male_ru_voice_found:
        for voice in voices:
            if 'russian' in voice.name.lower() or 'ru' in voice.id.lower():
                engn.setProperty('voice', voice.id)
                logger.info(f"Установлен русский голос: {voice.name}")
                break

    # Выводим список всех доступных голосов для отладки
    logger.info("Доступные голоса:")
    for i, voice in enumerate(voices):
        gender = voice.gender if hasattr(voice, 'gender') else 'неизвестно'
        logger.info(f"Голос {i}: {voice.name}, ID: {voice.id}, Пол: {gender}")

    logger.info("Движок синтеза речи успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации движка синтеза речи: {e}")

# Флаг для прерывания озвучивания
speaking_flag = threading.Event()
speaking_flag.clear()

#voice acting
def speaker(text):
    """Озвучивание текста с возможностью прерывания"""
    try:
        # Если уже идет озвучивание, прерываем его
        if speaking_flag.is_set():
            engn.stop()
            speaking_flag.clear()
            logger.info("Предыдущее озвучивание прервано")

        # Устанавливаем флаг озвучивания
        speaking_flag.set()

        # Выводим текст в консоль
        print(f"Алекс: {text}")

        # Озвучиваем текст
        engn.say(text)
        engn.runAndWait()

        # Сбрасываем флаг озвучивания
        speaking_flag.clear()

        logger.info(f"Озвучено: {text[:50]}...")
    except Exception as e:
        logger.error(f"Ошибка озвучивания: {e}")
        speaking_flag.clear()


#greeting
def speak(what):
    """Альтернативная функция озвучивания с выводом в консоль"""
    try:
        print(f"Алекс: {what}")

        # Если уже идет озвучивание, прерываем его
        if speaking_flag.is_set():
            engn.stop()
            speaking_flag.clear()

        # Устанавливаем флаг озвучивания
        speaking_flag.set()

        engn.say(what)
        engn.runAndWait()
        engn.stop()

        # Сбрасываем флаг озвучивания
        speaking_flag.clear()

        logger.info(f"Озвучено через speak: {what[:50]}...")
    except Exception as e:
        logger.error(f"Ошибка в функции speak: {e}")
        speaking_flag.clear()


def indicate_listening(status=True):
    """Индикация активного слушания"""
    if status:
        print("🎤 Слушаю...")
    else:
        print("🔇 Ожидание...")
