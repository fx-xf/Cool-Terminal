import os
import queue
import sounddevice as sd
import vosk
import random
import json
import threading
import subprocess
import GPUtil
import platform
import re
import time
import shutil
import datetime
import socket
import webbrowser
import psutil
from pydub import AudioSegment
from pydub.playback import play
from data import (
    YES, STOP, MY_NAME, PLEASE, PLAYING, PERVERT, OPEN, OK, HURRAY, HOW_ARE_YOU, HI, HELP, FUU, FEET, ANIME, ACTION, ACTION18,
    PHRASE_HI, PHRASE_MY_NAME, PHRASE_NEW_IMG, PHRASE_OPEN_YOUTUBE, PHRASE_TURN_ANIME, PHRASE_OFF_PC, PHRASE_PLAY_MUSIC, PHRASE_HIDDEN_IMG
)
from arts import anime, programming, cyberpunk, feet, gamer, minecraft, soulsborn

# Путь к модели Vosk для распознавания речи
MODEL_PATH = "vosk-model-small-ru-0.22"

# Частота дискретизации и количество каналов для записи
SAMPLE_RATE = 44100  # Частота дискретизации 44100 Гц
CHANNELS = 1  # Одноканальная запись (моно)

# Создаем очередь для хранения аудио данных
q = queue.Queue()

def callback(indata, frames, time, status):
    """
    Колбек функция для записи звука. Вызывается каждый раз, когда записываются новые данные.
    """
    if status:
        print(f"Статус: {status}", flush=True)
    q.put(bytes(indata))

def ansi_color(r, g, b):
    """
    Возвращает строку ANSI для установки цвета текста в терминале.
    """
    return f'\033[38;2;{r};{g};{b}m'

reset = '\033[0m'  # Сброс цвета в терминале

def hex_to_rgb(hex_color):
    """
    Преобразует цвет в формате HEX в формат RGB.
    """
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def html_to_ansi(html_content):
    """
    Преобразует HTML-контент с цветными тегами в ANSI-коды для терминала.
    """
    pre_content_pattern = re.compile(r'<pre[^>]*>(.*?)</pre>', re.DOTALL)
    b_tag_pattern = re.compile(r'<b style="color:#([0-9A-Fa-f]{6})">(.*?)</b>', re.DOTALL)

    pre_content_match = pre_content_pattern.search(html_content)
    if pre_content_match:
        pre_content = pre_content_match.group(1)

        def replace_b_tag(match):
            hex_color, text = match.groups()
            r, g, b = hex_to_rgb(hex_color)
            return f'{ansi_color(r, g, b)}{text}{reset}'

        result = b_tag_pattern.sub(replace_b_tag, pre_content)
        result = re.sub(r'^\s+', '', result, flags=re.MULTILINE)

        return result
    else:
        return "No <pre> content found"

def create_system_diagrams(term_width):
    """
    Создает текстовые диаграммы для загруженности системы.
    """
    # Получаем загруженность CPU и GPU
    cpu_percent = int(psutil.cpu_percent(interval=1))
    gpu_percent = int(get_gpu_usage())  # Функция для получения загрузки GPU, если поддерживается

    # Получаем данные о диске
    disk_usage = int(get_disk_usage())
    
    # Получаем сетевую активность
    net_sent, net_recv = get_network_speed()
    net_speed_diagram = f"Net Speed: {net_sent / 1024:.2f} KB sent / {net_recv / 1024:.2f} KB recv"

    # Получаем температуру
    cpu_temp = get_cpu_temperature()
    gpu_temp = get_gpu_temperature()
    temp_diagram = f"Temp: {cpu_temp}, {gpu_temp}"

    # Получаем заряд батареи
    battery_percent = int(get_battery_percentage())
    battery_diagram = f"Battery: {battery_percent}%"

    cpu_info = get_cpu_info()
    cpu_info_diagram = f"CPU Information: {cpu_info}"

    gpu_info = get_gpu_info()
    gpu_info_diagram = f"GPU Information: {gpu_info}"

    os, release, version, machine = get_os_info()
    os_information_diagram = f'OS: {os}, Release: {release}, Version: {version}, Machine: {machine}'

    name, terminal, host, time = get_logged_in_users()
    user_info_diagram = f'User name: {name}, Terminal: {terminal}, User host: {host}, Login time: {time}'

    # Формируем строки диаграмм
    def create_diagram(label, value, max_width):
        return f"{label}: [{'#' * (value // 2)}{' ' * (max_width - (value // 2))}] {value}%"

    max_diagram_width = term_width - 1

    cpu_diagram = create_diagram("CPU", cpu_percent, 50)
    gpu_diagram = create_diagram("GPU", gpu_percent, 50)
    disk_diagram = create_diagram("Disk", disk_usage, 49)

    return cpu_diagram, gpu_diagram, disk_diagram, net_speed_diagram, temp_diagram, battery_diagram, cpu_info_diagram, gpu_info_diagram, os_information_diagram, user_info_diagram

def print_content_with_timer_and_rates(content):
    """
    Выводит контент в терминал с учетом текущего размера терминала, диаграммы размещаются справа от основного контента.
    """
    term_width, term_height = shutil.get_terminal_size()

    # Получаем диаграммы системы
    cpu_diagram, gpu_diagram, disk_diagram,  net_speed_diagram, temp_diagram, battery_diagram, cpu_info_diagram, gpu_info_diagram, os_information_diagram, user_info_diagram = create_system_diagrams(term_width)

    # Основной контент
    content_lines = content.split('\n')

    # Заполняем строки для основного контента
    output_lines = [''] * term_height

    # Добавляем основной контент и диаграммы справа
    for i in range(term_height):
        if i < len(content_lines):
            content_line = content_lines[i]
        else:
            content_line = ''
        
        if i == 0:  # Добавляем пустую строку сверху
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}"
        elif i == 1:  # В следующей строке добавляем диаграмму CPU
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}{cpu_diagram}"
        elif i == 2:  # В строке после диаграммы CPU добавляем диаграмму GPU
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}{gpu_diagram}"
        elif i == 3:  # В строке после диаграммы GPU добавляем диаграмму Disk
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}{disk_diagram}"
        elif i == 4:  # В строке после диаграммы Free Mem добавляем диаграмму Net Speed
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}{net_speed_diagram}"
        elif i == 5:  # В строке после диаграммы Net Speed добавляем диаграмму Temp
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}{temp_diagram}"
        elif i == 6:  # В строке после диаграммы Temp добавляем диаграмму Battery
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}{battery_diagram}"
        elif i == 7:
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}{cpu_info_diagram}"
        elif i == 8:
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}{gpu_info_diagram}"
        elif i == 9:
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}{os_information_diagram}"
        elif i == 10:
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}{user_info_diagram}"
        else:  # Остальные строки для основного контента
            output_lines[i] = f"{content_line:{term_width - len(cpu_diagram)}}"

    # Очистка экрана и вывод обновленного контента
    print("\033c", end="")
    print("\n".join(output_lines))

def get_disk_usage():
    """
    Получает данные о загруженности диска.
    """
    disk_usage = psutil.disk_usage('/')
    return int(disk_usage.percent)

def get_network_speed():
    """
    Получает данные о сетевой активности.
    """
    net_before = psutil.net_io_counters()
    time.sleep(1)  # Задержка для измерения
    net_after = psutil.net_io_counters()
    net_sent = net_after.bytes_sent - net_before.bytes_sent
    net_recv = net_after.bytes_recv - net_before.bytes_recv
    return net_sent, net_recv

def get_cpu_temperature():
    try:
        # Выполняем команду 'sensors' и получаем её вывод
        result = subprocess.run(['sensors'], stdout=subprocess.PIPE, text=True)
        output = result.stdout

        # Ищем строку с температурой процессора с использованием регулярных выражений
        match = re.search(r'Package id 0:\s+\+([\d\.]+)°C', output)
        if match:
            temp = match.group(1)
            return f"CPU Temperature: +{temp}°C"
        
        return "CPU temperature data not found."
    except Exception as e:
        return f"Error getting CPU temperature: {str(e)}"

def get_gpu_temperature():
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]  # Предположим, что у нас один GPU
            return f"GPU Temperature: {gpu.temperature}°C"
        else:
            return "No GPU found."
    except Exception as e:
        return f"Error getting GPU temperature: {str(e)}"

def get_battery_percentage():
    """
    Получает данные о заряде батареи.
    """
    battery = psutil.sensors_battery()
    return battery.percent if battery else 100

def get_gpu_usage():
    """
    Получает данные о загрузке GPU (заглушка, замените на реальную функцию).
    """
    return 0  # Замените на реальный метод получения загрузки GPU

def get_cpu_info():
    try:
        cpu_info = os.popen("lscpu | grep 'Model name:'").read().strip().split(":")[1].strip()
        return cpu_info
    except Exception as e:
        return f"Error retrieving CPU information: {e}"

def get_gpu_info():
    try:
        gpu_info = os.popen("lspci | grep -i 'vga\\|3d\\|2d'").read().strip().split("\n")
        gpus = [gpu.split(":")[2].strip() for gpu in gpu_info]
        return gpus
    except Exception as e:
        return [f"Error retrieving GPU information: {e}"]

def get_os_info():
    os = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    return os, release, version, machine

def get_logged_in_users():
    name = None
    terminal = None
    host = None
    time = None
    users = psutil.users()
    for user in users:
        name = user.name
        terminal = user.terminal
        host = user.host
        time = datetime.datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')
    return name, terminal, host, time 

def get_html_content():
    """
    Возвращает случайный HTML-контент из заданных коллекций.
    """
    num = random.randint(0, 5)
    choices = [anime, programming, cyberpunk, soulsborn, gamer, minecraft]
    return random.choice(choices[num])

def html_output_task(lock):
    """
    Задача для обновления и вывода HTML-контента в терминал.
    """
    global content
    last_update_perf_counter = time.perf_counter()

    while True:
        current_perf_counter = time.perf_counter()

        with lock:
            if (current_perf_counter - last_update_perf_counter) >= 300:
                content = html_to_ansi(get_html_content())
                last_update_perf_counter = current_perf_counter

            print_content_with_timer_and_rates(content)
        
        time.sleep(0.5)  # Задержка между итерациями

def voice_assistant_task(lock):
    """
    Задача для обработки голосовых команд и выполнения соответствующих действий.
    """
    global content
    # Загрузка модели Vosk
    if not os.path.exists(MODEL_PATH):
        print(f"Модель по пути {MODEL_PATH} не найдена.", flush=True)
        return

    model = vosk.Model(MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)

    # Запуск записи с микрофона
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8192, dtype='int16',
                           channels=CHANNELS, callback=callback, device='hw:1,0'):
        sound = AudioSegment.from_file(random.choice(HI))
        play(sound)
        sound = AudioSegment.from_file(random.choice(MY_NAME))
        play(sound)
        try:
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    text = json.loads(result).get("text", "")

                    if text in PHRASE_HI:
                        sound = AudioSegment.from_file(random.choice(HI))
                        play(sound)
                    elif text in PHRASE_MY_NAME:
                        sound = AudioSegment.from_file(random.choice(MY_NAME))
                        play(sound)
                    elif text in PHRASE_NEW_IMG:
                        with lock:
                            content = html_to_ansi(get_html_content())
                            print_content_with_timer_and_rates(content)
                            sound = AudioSegment.from_file(random.choice(ACTION))
                            play(sound)
                    elif text in PHRASE_OPEN_YOUTUBE:
                        webbrowser.open('https://www.youtube.com/')
                        sound = AudioSegment.from_file(random.choice(ACTION))
                        play(sound)
                    elif text in PHRASE_TURN_ANIME:
                        webbrowser.open('https://animego.org/?ysclid=lz760appjw159414894')
                        sound = AudioSegment.from_file(random.choice(ANIME))
                        play(sound)
                    elif text in PHRASE_PLAY_MUSIC:
                        webbrowser.open('https://music.yandex.ru/home')
                        sound = AudioSegment.from_file(random.choice(ACTION))
                        play(sound)
                    elif text in PHRASE_HIDDEN_IMG:
                        with lock:
                            content = html_to_ansi(random.choice(feet))
                            print_content_with_timer_and_rates(content)
                            sound = AudioSegment.from_file(random.choice(ACTION18))
                            play(sound)
                    elif text in PHRASE_OFF_PC:
                        sound = AudioSegment.from_file(random.choice(ACTION))
                        play(sound)
                        os.system('shutdown -h now')  # Выключение ПК
        except KeyboardInterrupt:
            print("\nПрограмма завершена пользователем.", flush=True)
        except Exception as e:
            print(f"Произошла ошибка: {e}", flush=True)

if __name__ == "__main__":
    # Инициализируем блокировку
    lock = threading.Lock()
    content = html_to_ansi(get_html_content())
    
    # Создаем и запускаем потоки
    html_thread = threading.Thread(target=html_output_task, args=(lock,))
    voice_thread = threading.Thread(target=voice_assistant_task, args=(lock,))

    html_thread.start()
    voice_thread.start()

    # Ожидаем завершения потоков
    html_thread.join()
    voice_thread.join()
