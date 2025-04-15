import cv2
from flask import Flask, Response, jsonify
import serial
import time
import struct
from threading import Thread
from flask_cors import CORS

app = Flask(__name__)

app(CORS)

cams = [
    cv2.VideoCapture(0),
]

ser_1 = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
ser_2 = serial.Serial('/dev/ttyUSB1', baudrate=9600, timeout=1)

total_load_1 = None
total_load_2 = None

READ_PROCESSED_DISTANCE = bytes([0x01, 0x03, 0x01, 0x00, 0x00, 0x01, 0x85, 0xF6])

def read_sensor(command,ser):
    ser.write(command)
    time.sleep(0.1)

    response = ser.read(7)  # Ожидаемая длина ответа: 7 байт
    if len(response) == 7 and response[0] == 0x01:  # Проверка ответа
        raw_value = response[3:5]  # Извлечение 2-байтовых данных
        value = struct.unpack('>H', raw_value)[0]  # Конвертация из big-endian
        return value
    else:
        print("Invalid response:", response.hex())
        return None

def update_sensor_data():
    global processed_distance_1,processed_distance_2, total_load_1, total_load_2
    while True:
        processed_distance_1 = read_sensor(READ_PROCESSED_DISTANCE,ser_1)
        processed_distance_2 = read_sensor(READ_PROCESSED_DISTANCE,ser_2)
        total_load_1 = round(processed_distance_1 / 100,2)
        total_load_2 = round(processed_distance_2 / 100,2)
        time.sleep(1)

def generate_feed(camera_index):
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
    if 0 <= cam_id < len(cams):
        return Response(generate_feed(cam_id), mimetype='multipart/x-mixed-replace; boundary=frame')
    return "Камера не найдена", 404

@app.route('/get_sensor_data')
def get_sensor_data():
    return jsonify({'sensor_data_4': processed_distance_1 if processed_distance_1 is not None else 0,
                    'sensor_data_5': processed_distance_2 if processed_distance_2 is not None else 0,
                    'total_load_1': total_load_1 if total_load_1 is not None else 0,
                    'total_load_2': total_load_2 if total_load_2 is not None else 0,
                    })

@app.route('/')
def index():
    camera_links = "<br>".join([f'<a href="/cam{i}">Камера {i}</a>' for i in range(len(cams))])
    sensor_link = '<br><a href="/get_sensor_data">Данные с датчика</a>'
    return camera_links + sensor_link

if __name__ == '__main__':
    Thread(target=update_sensor_data).start()

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
