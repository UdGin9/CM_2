import serial
import time
import struct
import random
from threading import Thread

class SensorReader:
    def __init__(self, port, baudrate, timeout, modbus_command, update_interval, use_mock=False):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.command = modbus_command
        self.update_interval = update_interval
        self.use_mock = use_mock
        self.processed_distance = None
        self.running = False
        self.thread = None

        if not use_mock:
            try:
                self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
            except Exception as e:
                print(f"Ошибка инициализации последовательного порта: {e}")
                self.use_mock = True

    def read_sensor(self):
        """Чтение данных с датчика через Modbus"""
        if self.use_mock:
            return random.uniform(0.5, 2.0)

        try:
            self.ser.write(self.command)
            time.sleep(0.1)
            response = self.ser.read(7)
            if len(response) == 7 and response[0] == 0x01:
                raw_value = response[3:5]
                value = struct.unpack('>H', raw_value)[0]
                return value
            else:
                print("Неверный ответ от датчика:", response.hex())
                return None
        except Exception as e:
            print(f"Ошибка чтения датчика: {e}")
            return None

    def update_loop(self):
        """Фоновый цикл обновления данных"""
        while self.running:
            self.processed_distance = self.read_sensor()
            time.sleep(self.update_interval)

    def start(self):
        """Запуск фонового потока"""
        self.running = True
        self.thread = Thread(target=self.update_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Остановка потока"""
        self.running = False
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()

    def get_data(self):
        """Получить текущее значение"""
        return self.processed_distance or 0.0

    def get_fluctuated_data(self):
        """Вернуть данные с небольшим шумом"""
        base = self.get_data()
        fluctuation = base * 0.03 * random.uniform(-1, 1)
        return round(base + fluctuation, 2)