from config.configuration import WLAN_SSID, WLAN_PASSWORD, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC
from micropython import const
from urandom import randint
from network import WLAN, STA_IF
from umqtt.simple import MQTTClient
from utime import sleep_ms


MQTT_CLIENT_ID = f'publisher-{randint(0, 1000)}'

MAX_VALUE = const(135)
MIN_VALUE = const(45)
STEP = const(1)
DELAY = const(25)


def on_publish(clint, topic, payload) -> None:
    """
    Publishes message to MQTT
    :param clint: mqtt client
    :param topic: mqtt topic
    :param payload: mqtt payload
    :return: None
    """
    clint.publish(topic, payload.encode())


def generate_numbers(minimum, maximum, step):
    """
    Generates a numbers between minimum and maximum by step
    :param minimum: number for minimum
    :param maximum: number for maximum
    :param step: step between numbers
    :return: number value as int
    """
    num = minimum
    direction = 1

    while True:
        yield num
        num += step * direction

        if num > maximum:
            direction = -1
            num = maximum
        elif num < minimum:
            direction = 1
            num = minimum


if __name__ == '__main__':
    sta = WLAN(STA_IF)
    sta.active(True)
    sta.connect(WLAN_SSID, WLAN_PASSWORD)

    while not sta.isconnected():
        print(f'[INFO] Connection to {WLAN_SSID}')

    config = sta.ifconfig()

    print(f'[INFO] connected to WLAN {WLAN_SSID}')

    print(f'[INFO] connecting to MQTT')
    client = MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_BROKER, port=MQTT_PORT)
    client.connect()

    generator = generate_numbers(MIN_VALUE, MAX_VALUE, STEP)

    print(f'[INFO] send messages to MQTT')
    while True:
        angle = next(generator)
        distance = randint(150, 200)

        on_publish(clint=client, topic=MQTT_TOPIC, payload=f'{int(angle)};{int(distance)}')
        sleep_ms(DELAY)
