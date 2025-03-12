#!/usr/bin/env python3
import subprocess
import sys
import zipfile
from pathlib import Path

import requests


def install_package(package):
    """Установка пакета через pip"""
    print(f"Установка пакета {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def download_file(url, destination):
    """Скачивание файла с прогресс-баром"""
    print(f"Скачивание {url} в {destination}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte

    with open(destination, 'wb') as file:
        for data in response.iter_content(block_size):
            file.write(data)
            # Простой прогресс-бар
            sys.stdout.write('\r{0:.1f}%'.format(file.tell() * 100 / total_size))
            sys.stdout.flush()
    print()  # Новая строка после прогресс-бара

def main():
    """Основная функция установки"""
    print("Начинаем установку Vosk TTS и скачивание модели для русского языка...")

    # Установка vosk-tts
    try:
        install_package("vosk-tts")
        print("Пакет vosk-tts успешно установлен")
    except Exception as e:
        print(f"Ошибка при установке vosk-tts: {e}")
        return

    # Скачивание модели
    model_dir = Path("vosk-model-tts-ru-0.7-multi")
    if model_dir.exists():
        print(f"Модель {model_dir} уже существует. Пропускаем скачивание.")
    else:
        # URL модели (замените на актуальный)
        model_url = "https://alphacephei.com/vosk/models/vosk-model-tts-ru-0.7-multi.zip"
        zip_path = Path("vosk-model-tts-ru-0.7-multi.zip")

        try:
            # Скачивание архива
            download_file(model_url, zip_path)

            # Распаковка архива
            print(f"Распаковка архива {zip_path}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")

            # Удаление архива
            print(f"Удаление архива {zip_path}...")
            zip_path.unlink()

            print(f"Модель успешно скачана и распакована в {model_dir}")
        except Exception as e:
            print(f"Ошибка при скачивании или распаковке модели: {e}")
            return

    print("\nУстановка завершена! Теперь вы можете использовать Vosk TTS с мужским голосом.")
    print("Для тестирования запустите: python vosk_voice.py")

if __name__ == "__main__":
    main()
