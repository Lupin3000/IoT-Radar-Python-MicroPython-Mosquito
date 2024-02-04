from tkinter import Tk, Canvas, BOTH
from math import cos, sin, radians


class Radar:
    """
    Radar class to represent a Radar UI via a Tk interface
    """

    _DISTANCE: str = "cm"
    _FONT: str = "Helvetica"
    _COLORS: dict = {
        'radar': 'white',
        'background': 'black',
        'point': 'cornflower blue',
        'line': 'lawn green',
        'line_text': 'cyan'
    }
    _ARC_STEPS: int = 3
    _SONAR_OBJECTS: dict = {}

    def __init__(self, screen_width: int, screen_height: int, title: str) -> None:
        """
        Radar UI interface constructor
        :param screen_width: width of the screen
        :param screen_height: height of the screen
        """
        self._screen_width = int(screen_width)
        self._screen_height = int(screen_height)
        self._center_x = self._screen_width // 2
        self._center_y = self._screen_height - 50
        self._line_width = None
        self._angle_start = None
        self._angle_end = None
        self._max_radius = None
        self._arc_distance = None

        self.screen = Tk()
        self.screen.title(str(title))
        self.screen.geometry(f'{self._screen_width}x{self._screen_height}+0+0')
        self.screen.resizable(width=False, height=False)

        self.canvas = Canvas(self.screen, bg=self._COLORS['background'])
        self.canvas.pack(expand=True, fill=BOTH)

    def configure(self, line_width: int, max_radius: int, arc_distance: int, start_angle: int, end_angle: int) -> None:
        """
        Configure the radar
        :param line_width: line width of the graphics
        :param max_radius: arc max radius
        :param arc_distance: arc distance in pixel
        :param start_angle: start angle in degrees for arcs
        :param end_angle: end angle in degrees for arcs
        :return: None
        """
        self._line_width = int(line_width)
        self._angle_start = int(start_angle)
        self._angle_end = int(end_angle)
        self._max_radius = int(max_radius)
        self._arc_distance = int(arc_distance)

    def _draw_line(self, angle: int, color: str) -> None:
        """
        Draw line with given angle and color on interface
        :param angle: angle in degrees
        :return: None
        """
        in_radian = radians(int(angle))
        x1 = self._center_x
        y1 = self._center_y
        x2 = x1 + self._max_radius * cos(in_radian)
        y2 = y1 - self._max_radius * sin(in_radian)

        self.canvas.create_line(x1, y1, x2, y2, width=self._line_width, fill=str(color))

    def _draw_text(self, x: int, y: int, text: str, color: str, font_size: int = 20) -> None:
        """
        Draw given text with values on interface
        :param x: x position as integer
        :param y: y position as integer
        :param text: string with current line angle
        :param color: color of the text as string
        :param font_size: optional font size (default: 20)
        :return: None
        """
        x_pos = int(x)
        y_pos = int(y)
        font = (self._FONT, int(font_size))

        self.canvas.create_text(x_pos, y_pos, text=str(text), font=font, fill=color)

    def _draw_background(self, show_measurement: bool = True) -> None:
        """
        Draw radar background graphic on interface
        :param show_measurement: whether to show the measurement or not
        :return: None
        """
        color = self._COLORS['radar']
        angle_total = self._angle_start + self._angle_end
        x1 = self._center_x - self._max_radius
        y1 = self._center_y - self._max_radius
        x2 = self._center_x + self._max_radius
        y2 = self._center_y + self._max_radius

        for _ in range(self._ARC_STEPS):
            self.canvas.create_arc(x1, y1, x2, y2,
                                   start=self._angle_start,
                                   extent=self._angle_end,
                                   width=self._line_width,
                                   outline=color)

            x1 += self._arc_distance
            y1 += self._arc_distance
            x2 -= self._arc_distance
            y2 -= self._arc_distance

        for value in range(0, 360, 45):
            if self._angle_start <= value <= angle_total:
                self._draw_line(angle=value, color=color)

        radius = self._max_radius

        if bool(show_measurement):
            for _ in range(self._ARC_STEPS):
                text_start_x = self._center_x + radius * cos(radians(self._angle_start))
                text_start_y = self._center_y - radius * sin(radians(self._angle_start))
                text_end_x = self._center_x + radius * cos(radians(angle_total))
                text_end_y = self._center_y - radius * sin(radians(angle_total))

                if self._angle_start == 0:
                    text_start_x -= 25
                    text_start_y += 10

                if angle_total == 180:
                    text_end_x += 25
                    text_end_y += 10

                if self._angle_start <= 90:
                    text_start_x += 25

                if angle_total >= 90:
                    text_end_x -= 25

                self._draw_text(x=text_start_x,
                                y=text_start_y,
                                text=f'{radius}{self._DISTANCE}',
                                color=color,
                                font_size=10)

                self._draw_text(x=text_end_x,
                                y=text_end_y,
                                text=f'{radius}{self._DISTANCE}',
                                color=color,
                                font_size=10)

                radius -= self._arc_distance

    def _draw_point(self, distance: int, angle: int) -> None:
        """
        Draw point on radar with given distance and angle on interface
        :param distance: distance in centimeters
        :param angle: angle in degrees
        :return: None
        """
        color = self._COLORS['point']

        in_radian = radians(int(angle))
        x = self._center_x + int(distance) * cos(in_radian)
        y = self._center_y - int(distance) * sin(in_radian)

        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color)

    def update(self, distance: int, angle: int) -> None:
        """
        Update the radar with given distance and angle
        :param distance: distance in centimeters
        :param angle: angle in radian
        :return: None
        """
        current_distance = int(distance)
        current_angle = int(angle)

        self._SONAR_OBJECTS[angle] = current_distance
        end = self._angle_start + self._angle_end

        self.canvas.delete("all")

        self._draw_background()
        self._draw_text(x=self._center_x,
                        y=self._center_y + 15,
                        text=f'{current_angle}°',
                        color=self._COLORS['line_text'])

        for key, value in self._SONAR_OBJECTS.items():
            if 1 <= value <= self._max_radius and self._angle_start <= key <= end:
                self._draw_point(distance=value, angle=key)

        if self._angle_start <= current_angle <= end:
            self._draw_line(angle=current_angle, color=self._COLORS['line'])
