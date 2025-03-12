import logging
import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path

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
logger = logging.getLogger('vosk_voice')

# Флаг для прерывания озвучивания
speaking_flag = threading.Event()
speaking_flag.clear()

# Проверка наличия vosk-tts
try:
    import importlib.util
    vosk_tts_installed = importlib.util.find_spec("vosk_tts") is not None
    if not vosk_tts_installed:
        logger.warning("Библиотека vosk-tts не установлена. Используйте 'pip install vosk-tts' для установки.")
except Exception as e:
    logger.error(f"Ошибка при проверке наличия vosk-tts: {e}")
    vosk_tts_installed = False

# Проверка наличия модели
model_path = Path('vosk-model-tts-ru-0.7-multi')
if not model_path.exists():
    logger.warning(f"Модель {model_path} не найдена. Скачайте модель с https://alphacephei.com/vosk/models")

# Инициализация Vosk TTS, если установлен
vosk_synth = None
if vosk_tts_installed:
    try:
        from vosk_tts import Model, Synth
        if model_path.exists():
            model = Model(model_name=str(model_path))
            vosk_synth = Synth(model)
            logger.info("Vosk TTS успешно инициализирован")
        else:
            logger.warning("Модель для Vosk TTS не найдена")
    except Exception as e:
        logger.error(f"Ошибка инициализации Vosk TTS: {e}")
        vosk_synth = None

# Настройка резервного синтезатора речи (pyttsx3)
try:
    import pyttsx3
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

    logger.info("Резервный движок синтеза речи успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации резервного движка синтеза речи: {e}")
    engn = None

def play_audio(file_path):
    """Воспроизведение аудио файла"""
    try:
        if os.name == 'posix':  # Linux/Mac
            subprocess.run(['afplay', file_path], check=True)
        else:  # Windows
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
        return True
    except Exception as e:
        logger.error(f"Ошибка воспроизведения аудио: {e}")
        return False

def speaker(text):
    """Озвучивание текста с возможностью прерывания"""
    try:
        # Если уже идет озвучивание, прерываем его
        if speaking_flag.is_set():
            speaking_flag.clear()
            logger.info("Предыдущее озвучивание прервано")
            time.sleep(0.1)  # Даем время на завершение предыдущего процесса

        # Устанавливаем флаг озвучивания
        speaking_flag.set()

        # Выводим текст в консоль
        print(f"Алекс: {text}")

        # Пытаемся использовать Vosk TTS с мужским голосом (speaker_id=2 или 3)
        if vosk_synth:
            try:
                # Создаем временный файл для аудио
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_path = temp_file.name

                # Синтезируем речь с мужским голосом (speaker_id=2 или 3 для мужских голосов)
                vosk_synth.synth(text, temp_path, speaker_id=3)  # Можно попробовать 2 или 3

                # Воспроизводим аудио
                success = play_audio(temp_path)

                # Удаляем временный файл
                try:
                    os.unlink(temp_path)
                except:
                    pass

                if success:
                    speaking_flag.clear()
                    logger.info(f"Озвучено через Vosk TTS: {text[:50]}...")
                    return
            except Exception as e:
                logger.error(f"Ошибка при использовании Vosk TTS: {e}")

        # Если Vosk TTS не сработал, используем pyttsx3
        if engn:
            engn.say(text)
            engn.runAndWait()
            logger.info(f"Озвучено через pyttsx3: {text[:50]}...")
        else:
            logger.error("Не удалось озвучить текст: нет доступных синтезаторов речи")

        # Сбрасываем флаг озвучивания
        speaking_flag.clear()
    except Exception as e:
        logger.error(f"Ошибка озвучивания: {e}")
        speaking_flag.clear()

def speak(what):
    """Альтернативная функция озвучивания с выводом в консоль"""
    speaker(what)

def indicate_listening(status=True):
    """Индикация активного слушания"""
    if status:
        print("🎤 Слушаю...")
    else:
        print("🔇 Ожидание...")

# Тестирование, если файл запущен напрямую
if __name__ == "__main__":
    speaker("Привет! Я голосовой помощник Алекс с мужским голосом. Тестирую синтез речи.")
