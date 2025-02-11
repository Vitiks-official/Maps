from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import requests
import sys
import os


class MainWindow(QMainWindow):
    STATIC_API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
    STATIC_SERVER = "http://static-maps.yandex.ru/v1"

    GEO_API_KEY = "4a62aa4a-8d1c-4533-81cf-9c18ef1eb784"
    GEO_SERVER = "http://geocode-maps.yandex.ru/1.x"

    SEARCH_API_KEY = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    SEARCH_SERVER = "https://search-maps.yandex.ru/v1"

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Карты")
        self.setFixedSize(800, 600)

        self.pixmap = QPixmap()

        self.map_label = QLabel(self)
        self.map_label.setGeometry(200, 20, 400, 400)
        self.map_label.setPixmap(self.pixmap)

        self.curr_pos = [55.62264, 40.68533]
        self.curr_zoom = 17

        self.load_map()

    def load_map(self):
        str_pos = ",".join(list(map(str, self.curr_pos[::-1])))
        params = {"apikey": self.STATIC_API_KEY,
                  "ll": str_pos,
                  "z": self.curr_zoom}
        response = requests.get(self.STATIC_SERVER, params=params)
        if not response:
            print(f"Static API Error: {response.status_code}")
            sys.exit()
        with open("map.png", "wb") as file:
            file.write(response.content)
        self.pixmap = QPixmap.fromImage(QImage("map.png"))
        self.map_label.setPixmap(self.pixmap)
        os.remove("map.png")

    def keyPressEvent(self, event):
        print(self.curr_pos)
        move = 0.00001 * 2 ** (22 - self.curr_zoom)
        if event.key() == Qt.Key.Key_PageUp and self.curr_zoom < 21:
            self.curr_zoom += 1
        elif event.key() == Qt.Key.Key_PageDown and self.curr_zoom > 0:
            self.curr_zoom -= 1
        elif event.key() == Qt.Key.Key_Up and abs(self.curr_pos[0] + move) < 90:
            self.curr_pos[0] += move
        elif event.key() == Qt.Key.Key_Down and abs(self.curr_pos[0] - move) < 90:
            self.curr_pos[0] -= move
        elif event.key() == Qt.Key.Key_Right and abs(self.curr_pos[1] + move) < 180:
            self.curr_pos[1] += move
        elif event.key() == Qt.Key.Key_Left and abs(self.curr_pos[1] - move) < 180:
            self.curr_pos[1] -= move
        else:
            return None

        self.load_map()


