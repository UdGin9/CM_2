from flask import Flask, jsonify, Response
from flask_cors import CORS
import threading

from config import CAMERA_IDS, FLASK_PORT, USE_MOCK_SENSOR, READ_PROCESSED_DISTANCE
from modules.camera_stream import CameraStream
from modules.sensor_reader import SensorReader

app = Flask(__name__)
CORS(app)

camera_stream = CameraStream(CAMERA_IDS)
sensor_reader_1 = SensorReader(
    port='/dev/ttyUSB0',
    baudrate=9600,
    timeout=1,
    modbus_command=READ_PROCESSED_DISTANCE,
    update_interval=3,
    use_mock=USE_MOCK_SENSOR
)
sensor_reader_2 = SensorReader(
    port='/dev/ttyUSB1',
    baudrate=9600,
    timeout=1,
    modbus_command=READ_PROCESSED_DISTANCE,
    update_interval=3,
    use_mock=USE_MOCK_SENSOR
)

sensor_reader_1.start()
sensor_reader_2.start()

@app.route('/cam<int:cam_id>')
def video_feed(cam_id):
    if 0 <= cam_id < camera_stream.get_camera_count():
        return Response(camera_stream.generate_feed(cam_id),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    return "Камера не найдена", 404

@app.route('/get_sensor_data')
def get_sensor_data():
    data = {
        'sensor_data_1': sensor_reader_1.get_data(),
        'sensor_data_2': sensor_reader_2.get_data(),
    }
    return jsonify(data)

@app.route('/')
def index():
    camera_links = "<br>".join([f'<a href="/cam{i}">Камера {i}</a>' for i in range(camera_stream.get_camera_count())])
    sensor_link = '<br><a href="/get_sensor_data">Данные с датчика</a>'
    return f"<h2>Вспомогательный сервер - RPi 3</h2>{camera_links}{sensor_link}"

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=FLASK_PORT, debug=False, threaded=True)
    finally:
        camera_stream.release()
        sensor_reader_1.stop()
        sensor_reader_2.stop()