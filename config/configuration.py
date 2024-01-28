# subscriber configuration (radar.py)
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400

ARC_CENTER_X = WINDOW_WIDTH // 2
ARC_CENTER_Y = WINDOW_HEIGHT - 50
ARC_RADIUS = 325
ARC_START = 45
ARC_EXTENT = 90
ARC_WIDTH = 1
ARC_STEPS = 100

# publisher configuration (main.py)

WLAN_SSID = ''
WLAN_PASSWORD = ''

# broker configuration (radar.py & main.py)

MQTT_BROKER = ''
MQTT_PORT = 1883
MQTT_TOPIC = "python/mqtt"
