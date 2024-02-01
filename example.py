from random import randint
from re import match
from paho.mqtt.client import Client
from config.configuration import (WINDOW_WIDTH, WINDOW_HEIGHT, ARC_RADIUS, ARC_START, ARC_EXTENT, ARC_WIDTH,
                                  MQTT_BROKER, MQTT_PORT, MQTT_TOPIC)
from lib.radar import Radar


MQTT_SUBSCRIBER_CLIENT_ID = f'subscriber-{randint(0, 1000)}'


def verify_and_split(input_string: str) -> dict:
    """
    Verifies that the input string matches the needed format
    :param input_string: mqtt message as string
    :return: dict with values for degree and distance
    """
    pattern = r"([0-9]\d*);([0-9]\d*)"
    check = match(pattern, input_string)

    if check:
        numbers_dict = {"degree": int(check.group(1)), "distance": int(check.group(2))}
        return numbers_dict
    else:
        return {'degree': False, 'distance': False}


def on_message(client, userdata, message) -> None:
    """
    Callback function for MQTT messages
    :param client: mqtt client
    :param userdata: mqtt userdata
    :param message: mqtt message
    :return: None
    """
    global radar

    _ = client
    _ = userdata
    msg = str(message.payload.decode("utf-8"))

    values = verify_and_split(msg)
    if not values['distance'] and not values['degree']:
        print('[Error] message does not match expected values "degrees;distance"')
    else:
        print(f"[Info] distance: {values['distance']}cm angle: {values['degree']}deg")

        radar.update(angle=values['degree'], distance=values['distance'])


if __name__ == '__main__':
    radar = Radar(screen_width=WINDOW_WIDTH,
                  screen_height=WINDOW_HEIGHT,
                  title="IoT MQTT Radar")

    radar.configure(line_width=ARC_WIDTH,
                    max_radius=ARC_RADIUS,
                    arc_distance=125,
                    start_angle=ARC_START,
                    end_angle=ARC_EXTENT)

    radar.update(distance=0, angle=45)

    try:
        print('[Info] Start MQTT connection and subscription]')
        mq_client = Client(MQTT_SUBSCRIBER_CLIENT_ID)
        mq_client.on_message = on_message
        mq_client.connect(MQTT_BROKER, MQTT_PORT)
        mq_client.subscribe(MQTT_TOPIC)
        mq_client.loop_start()
    except Exception as err:
        print(f'[Error] MQTT: {err}')

    radar.screen.mainloop()
