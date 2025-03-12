import json
import logging
import os
import queue
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
import vosk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

import words
# Заменяем импорт из voice на vosk_voice
# from tasks import *
from tasks import (browser, game, joke, news, nowtime, offPC, offtop, offVH,
                   reference, restartPC, salute, watchfilm, watchYT, weather)
# Импортируем функции из vosk_voice
from vosk_voice import indicate_listening, speak, speaker

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
logger = logging.getLogger('voice_helper')

q = queue.Queue()

# Загрузка модели распознавания речи
try:
    model = vosk.Model('big_model')
    logger.info("Модель распознавания речи успешно загружена")
except Exception as e:
    logger.error(f"Ошибка загрузки модели распознавания речи: {e}")
    speaker("Ошибка загрузки модели распознавания речи. Проверьте наличие модели и перезапустите программу.")
    exit(1)

# Настройка аудио устройства
try:
    device = sd.default.device  # default device
    samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])
    logger.info(f"Аудио устройство настроено: {device}, частота дискретизации: {samplerate}")
except Exception as e:
    logger.error(f"Ошибка настройки аудио устройства: {e}")
    speaker("Ошибка настройки аудио устройства. Проверьте подключение микрофона и перезапустите программу.")
    exit(1)

# Контекст для хранения предыдущих запросов и состояния
context = {
    'last_request': None,
    'last_response': None,
    'current_state': 'idle',  # idle, listening, processing
    'conversation_history': [],
    'confidence_threshold': 0.6  # Порог уверенности для распознавания команд
}

def callback(indata, frames, time, status):
    """Callback для аудио потока"""
    if status:
        logger.warning(f"Статус аудио потока: {status}")
    q.put(bytes(indata))

def preprocess_text(text):
    """Предобработка текста для улучшения распознавания"""
    # Приведение к нижнему регистру
    text = text.lower()
    # Удаление лишних пробелов
    text = ' '.join(text.split())
    return text

def get_command_similarity(text, commands):
    """Вычисление схожести текста с командами"""
    vectorizer = CountVectorizer().fit(list(commands) + [text])
    vectors = vectorizer.transform(list(commands) + [text]).toarray()
    text_vector = vectors[-1]
    command_vectors = vectors[:-1]

    # Вычисление косинусного сходства
    similarities = cosine_similarity([text_vector], command_vectors)[0]
    return similarities

def recognize(json_d, vectorizer, clf):
    """Распознавание команды из текста"""
    try:
        # Предобработка текста
        json_d = preprocess_text(json_d)
        logger.info(f"Распознанный текст: {json_d}")

        # Проверка на наличие имени помощника
        trg = words.NAMES.intersection(json_d.split())
        if not trg:
            # Если имя не найдено, но мы в режиме диалога, продолжаем обработку
            if context['current_state'] == 'conversation':
                logger.info("Продолжение диалога без упоминания имени")
            else:
                logger.info("Имя помощника не найдено в запросе")
                return

        # Удаление имени из запроса
        if trg:
            json_d = json_d.replace(list(trg)[0], '').strip()
            # Переход в режим диалога
            context['current_state'] = 'conversation'
            # Сброс режима диалога через 30 секунд бездействия
            # (в реальном приложении нужно реализовать таймер)

        # Сохранение запроса в контексте
        context['last_request'] = json_d
        context['conversation_history'].append(('user', json_d))

        # Если запрос пустой после удаления имени, используем приветствие
        if not json_d.strip():
            salute()
            return

        # Вычисление схожести с известными командами
        command_similarities = get_command_similarity(json_d, words.set_data.keys())
        max_similarity_idx = np.argmax(command_similarities)
        max_similarity = command_similarities[max_similarity_idx]

        logger.info(f"Максимальная схожесть: {max_similarity} с командой: {list(words.set_data.keys())[max_similarity_idx]}")

        # Если схожесть выше порога, используем найденную команду
        if max_similarity >= context['confidence_threshold']:
            command = list(words.set_data.keys())[max_similarity_idx]
            answer = words.set_data[command]
            logger.info(f"Выбрана команда: {command}, ответ: {answer}")
        else:
            # Иначе используем векторизатор и классификатор
            vector_text = vectorizer.transform([json_d]).toarray()[0]
            answer = clf.predict([vector_text])[0]
            logger.info(f"Классификатор выбрал ответ: {answer}")

        # Извлечение имени функции и выполнение
        func_name = answer.split()[0]
        response_text = answer.replace(func_name, '').strip()

        # Сохранение ответа в контексте
        context['last_response'] = response_text
        context['conversation_history'].append(('assistant', response_text))

        # Озвучивание ответа
        speaker(response_text)

        # Выполнение функции
        try:
            # Проверка наличия аргументов в запросе
            if 'погода' in json_d and 'завтра' in json_d:
                exec(f"{func_name}(days=2)")
            elif 'погода' in json_d and 'неделю' in json_d or 'погода' in json_d and 'недели' in json_d:
                exec(f"{func_name}(days=5)")
            elif 'новости' in json_d and 'спорт' in json_d:
                exec(f"{func_name}('спорт')")
            elif 'новости' in json_d and 'бизнес' in json_d:
                exec(f"{func_name}('бизнес')")
            elif 'новости' in json_d and 'технологии' in json_d:
                exec(f"{func_name}('технологии')")
            else:
                exec(f"{func_name}()")
        except Exception as e:
            logger.error(f"Ошибка выполнения функции {func_name}: {e}")
            speaker("Извините, произошла ошибка при выполнении команды.")

    except Exception as e:
        logger.error(f"Ошибка в функции recognize: {e}")
        speaker("Извините, я не смог распознать команду.")

#listening
def main():
    try:
        logger.info("Запуск голосового помощника")

        # Обучение классификатора
        vectorizer = CountVectorizer()
        vectors = vectorizer.fit_transform(list(words.set_data.keys()))
        clf = LogisticRegression()
        clf.fit(vectors, list(words.set_data.values()))
        logger.info("Классификатор успешно обучен")

        # Приветствие
        speaker("Привет! Я голосовой помощник Алекс.")

        # Запуск аудио потока
        with sd.RawInputStream(samplerate=samplerate, blocksize=48000, device=device[0], dtype='int16',
                              channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, samplerate)
            logger.info("Аудио поток запущен, ожидание команд")

            while True:
                try:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        result = rec.Result()
                        json_data = json.loads(result)

                        if 'text' in json_data and json_data['text'].strip():
                            recognize(json_data['text'], vectorizer, clf)
                except Exception as e:
                    logger.error(f"Ошибка в основном цикле: {e}")
                    continue

    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        speaker("Произошла критическая ошибка. Программа будет остановлена.")

if __name__ == '__main__':
    main()
