from pprint import pprint

from PyQt6.QtWidgets import QMainWindow, QLabel, QRadioButton, QPushButton, QTextBrowser
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from MyLineEdit import MyLineEdit
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

    LIGHT = "light"
    DARK = "dark"

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
        self.curr_theme = self.LIGHT
        self.curr_tag = ""

        self.address = MyLineEdit(self)
        self.address.setGeometry(140, 440, 520, 30)

        self.find_btn = QPushButton("Искать", self)
        self.find_btn.setGeometry(680, 440, 100, 30)
        self.find_btn.clicked.connect(self.find_address)

        self.reset_btn = QPushButton("Сброс", self)
        self.reset_btn.setGeometry(20, 440, 100, 30)
        self.reset_btn.clicked.connect(self.reset_result)

        self.address_browser = QTextBrowser(self)
        self.address_browser.setGeometry(20, 20, 160, 200)

        self.dark_theme = QRadioButton(self)
        self.dark_theme.setText("Тёмная тема")
        self.dark_theme.setGeometry(620, 50, 100, 30)
        self.dark_theme.clicked.connect(lambda: self.set_theme(self.DARK))
        self.dark_theme.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.light_theme = QRadioButton(self)
        self.light_theme.setText("Светлая тема")
        self.light_theme.setGeometry(620, 20, 100, 30)
        self.light_theme.clicked.connect(lambda: self.set_theme(self.LIGHT))
        self.light_theme.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.light_theme.setChecked(True)

        self.load_map()

    def set_theme(self, theme):
        self.curr_theme = theme
        self.load_map()

    def reset_result(self):
        self.curr_tag = ""
        self.load_map()

    def find_address(self):
        self.setFocus()
        geocode = self.address.text()
        if not geocode:
            return None
        params = {"apikey": self.GEO_API_KEY,
                  "geocode": geocode,
                  "format": "json"}
        response = requests.get(self.GEO_SERVER, params=params)
        if not response:
            print(f"Geocoder API Error: {response.status_code}")
            sys.exit()

        data = response.json()
        objects = data["response"]["GeoObjectCollection"]["featureMember"]
        if not objects:
            return None
        obj = objects[0]["GeoObject"]
        pos = obj["Point"]["pos"]
        address = obj["metaDataProperty"]["GeocoderMetaData"]["text"]
        self.address_browser.setText(address)
        self.curr_pos = [float(x) for x in pos.split()[::-1]]
        self.curr_tag = ",".join(pos.split()) + ",comma"
        self.load_map()

    def load_map(self):
        str_pos = ",".join(list(map(str, self.curr_pos[::-1])))
        params = {"apikey": self.STATIC_API_KEY,
                  "ll": str_pos,
                  "z": self.curr_zoom,
                  "theme": self.curr_theme,
                  "pt": self.curr_tag}
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
