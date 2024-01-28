from config.configuration import (WINDOW_WIDTH, WINDOW_HEIGHT, ARC_CENTER_X, ARC_CENTER_Y, ARC_RADIUS, ARC_START,
                                  ARC_EXTENT, ARC_WIDTH, ARC_STEPS, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC)
from tkinter import Tk, Canvas, BOTH
from math import cos, sin, radians
from paho.mqtt.client import Client
from re import match
from random import randint


MQTT_SUBSCRIBER_CLIENT_ID = f'subscriber-{randint(0, 1000)}'
SONAR_OBJECTS = {}


def draw_radar_bg(bg_canvas, center_x, center_y, radius, start, extend, arc_steps, arc_width) -> None:
    color = 'white'
    arc_x1 = center_x - radius
    arc_y1 = center_y - radius
    arc_x2 = center_x + radius
    arc_y2 = center_y + radius

    for _ in range(3):
        bg_canvas.create_arc(arc_x1, arc_y1, arc_x2, arc_y2, start=start, extent=extend, width=arc_width, outline=color)
        arc_x1 += arc_steps
        arc_y1 += arc_steps
        arc_x2 -= arc_steps
        arc_y2 -= arc_steps

    bg_canvas.create_text(center_x, center_y - 125 - 5, text='125cm', font=("Helvetica", 10), fill=color)
    bg_canvas.create_text(center_x, center_y - 225 - 5, text='225cm', font=("Helvetica", 10), fill=color)
    bg_canvas.create_text(center_x, center_y - 325 - 5, text='325cm', font=("Helvetica", 10), fill=color)


def draw_text(bg_canvas, x, y, text) -> None:
    color = 'cyan'
    bg_canvas.create_text(x, y, text=text, font=("Helvetica", 20), fill=color)


def draw_point(bg_canvas, x, y, distance, degree) -> None:
    color = 'cornflower blue'
    distance = int(distance)
    degree = int(degree)

    in_radian = radians(degree)
    point_x = x + distance * cos(in_radian)
    point_y = y - distance * sin(in_radian)

    bg_canvas.create_oval(point_x - 5, point_y - 5, point_x + 5, point_y + 5, fill=color)


def draw_radar_line(bg_canvas, center_x, center_y, radius, line_width, degree) -> None:
    color = 'lawn green'
    in_radian = radians(degree)
    line_x1 = center_x
    line_y1 = center_y
    line_x2 = line_x1 + radius * cos(in_radian)
    line_y2 = line_y1 - radius * sin(in_radian)

    bg_canvas.create_line(line_x1, line_y1, line_x2, line_y2, width=line_width, fill=color)


def update_screen(bg_canvas, center_x, center_y, radius, start, extent, steps, width, degree=45, distance=0) -> None:
    global SONAR_OBJECTS

    bg_canvas.delete("all")

    draw_radar_bg(bg_canvas=bg_canvas,
                  center_x=center_x,
                  center_y=center_y,
                  radius=radius,
                  start=start,
                  extend=extent,
                  arc_steps=steps,
                  arc_width=width)

    draw_text(bg_canvas=bg_canvas, x=center_x, y=center_y + 15, text=f'{degree}°')

    SONAR_OBJECTS[degree] = distance
    end = start + extent

    for key, value in SONAR_OBJECTS.items():
        if 1 <= value <= radius and start <= key <= end:
            draw_point(bg_canvas=bg_canvas, x=center_x, y=center_y, distance=value, degree=key)

    if start <= degree <= end:
        draw_radar_line(bg_canvas=bg_canvas,
                        center_x=center_x,
                        center_y=center_y,
                        radius=radius,
                        line_width=width,
                        degree=degree)


def verify_and_split(input_string) -> dict:
    pattern = r"([1-9]\d*);([1-9]\d*)"
    check = match(pattern, input_string)

    if check:
        numbers_dict = {"degree": int(check.group(1)), "distance": int(check.group(2))}
        return numbers_dict
    else:
        return {'degree': False, 'distance': False}


def on_message(client, userdata, message):
    _ = client
    _ = userdata

    msg = str(message.payload.decode("utf-8"))

    values = verify_and_split(msg)
    if not values['distance'] and not values['degree']:
        print('[Error] message does not match expected values "degrees;distance"')
    else:
        print(f"[Info] distance: {values['distance']}cm angle: {values['degree']}deg")

        update_screen(bg_canvas=canvas,
                      center_x=ARC_CENTER_X,
                      center_y=ARC_CENTER_Y,
                      radius=ARC_RADIUS,
                      start=ARC_START,
                      extent=ARC_EXTENT,
                      steps=ARC_STEPS,
                      width=ARC_WIDTH,
                      degree=values['degree'],
                      distance=values['distance'])


if __name__ == '__main__':
    window = Tk()
    window.title("IoT Radar")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+0+0")
    window.resizable(False, False)

    canvas = Canvas(window, bg='black')
    canvas.pack(expand=True, fill=BOTH)

    update_screen(bg_canvas=canvas,
                  center_x=ARC_CENTER_X,
                  center_y=ARC_CENTER_Y,
                  radius=ARC_RADIUS,
                  start=ARC_START,
                  extent=ARC_EXTENT,
                  steps=ARC_STEPS,
                  width=ARC_WIDTH)

    try:
        print('[Info] Start MQTT connection and subscription]')
        mq_client = Client(MQTT_SUBSCRIBER_CLIENT_ID)
        mq_client.on_message = on_message
        mq_client.connect(MQTT_BROKER, MQTT_PORT)
        mq_client.subscribe(MQTT_TOPIC)
        mq_client.loop_start()
    except Exception as err:
        print(f'[Error] MQTT: {err}')

    window.mainloop()
