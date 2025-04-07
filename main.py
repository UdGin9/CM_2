import cv2
from flask import Flask, Response, jsonify
import serial
import time
import struct
from threading import Thread

app = Flask(__name__)

# Настройка камер
cams = [
    cv2.VideoCapture(0),
]

# Настройка последовательного порта для датчика
# ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

# Modbus RTU запросы (hex)
# READ_PROCESSED_DISTANCE = bytes([0x01, 0x03, 0x01, 0x00, 0x00, 0x01, 0x85, 0xF6])

# Глобальный массив для хранения данных с датчика
# shared_array = []

# def read_sensor(command):
  #  """Отправка Modbus команды и чтение ответа"""
   # ser.write(command)  # Отправка Modbus команды
    #time.sleep(0.1)  # Ожидание ответа

    #response = ser.read(7)  # Ожидаемая длина ответа: 7 байт
    #if len(response) == 7 and response[0] == 0x01:  # Проверка ответа
     #   raw_value = response[3:5]  # Извлечение 2-байтовых данных
      #  value = struct.unpack('>H', raw_value)[0]  # Конвертация из big-endian
       # return value
    #else:
     #   print("Invalid response:", response.hex())
      #  return None

#def update_sensor_data():
 #   """Обновление данных с датчика каждую секунду"""
  #  global shared_array
   # while True:
    #    processed_distance = read_sensor(READ_PROCESSED_DISTANCE)
     #   if processed_distance is not None:
      #      shared_array.append(processed_distance)  # Обновление массива
       # time.sleep(1)  # Ожидание 1 секундуc

def generate_feed(camera_index):
    """Генерация видеопотока для камеры"""
    while True:
        success, frame = cams[camera_index].read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/cam<int:cam_id>')
def video_feed(cam_id):
    """Маршрут для вывода видеопотока"""
    if 0 <= cam_id < len(cams):
        return Response(generate_feed(cam_id), mimetype='multipart/x-mixed-replace; boundary=frame')
    return "Камера не найдена", 404

'''@app.route('/get_sensor_data')
def get_sensor_data():
    """Маршрут для получения данных с датчика"""
    return jsonify(shared_array)'''

@app.route('/')
def index():
    """Главная страница с ссылками на камеры и данные с датчика"""
    camera_links = "<br>".join([f'<a href="/cam{i}">Камера {i}</a>' for i in range(len(cams))])
    sensor_link = '<br><a href="/get_sensor_data">Данные с датчика</a>'
    return camera_links + sensor_link

if __name__ == '__main__':
    # Запуск потока для обновления данных с датчика
    # Thread(target=update_sensor_data).start()

    # Запуск Flask сервера
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
