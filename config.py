CAMERA_IDS = [0, 1]

FLASK_PORT = 15555

SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 9600
TIMEOUT = 1

READ_PROCESSED_DISTANCE = bytes([0x01, 0x03, 0x01, 0x00, 0x00, 0x01, 0x85, 0xF6])

SENSOR_UPDATE_INTERVAL = 3

USE_MOCK_SENSOR = False  # True — использовать случайные данные, False — читать с порта