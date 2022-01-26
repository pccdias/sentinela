"""Access IP Camera in Python OpenCV"""
# Página com o código: https://stackoverflow.com/questions/49978705/access-ip-camera-in-python-opencv

import cv2
import numpy as np
import datetime
from configparser import ConfigParser


class DvrIntelbras():

    def __init__(self):
        parser = ConfigParser()
        parser.read('config_DVR_intelbras.ini')
        self.user_password = parser.get('api_config', 'user_password')
        self.ip = parser.get('api_config', 'ip')
        self.port = parser.get('api_config', 'port')

    def set_uri(self, cam):
        p = str(self.user_password)
        uri = "rtsp://admin:" + str(
            self.user_password) + "@" + self.ip + ":" + self.port + "/cam/realmonitor?channel=" + str(
            cam) + "&subtype=0"
        return uri

    @staticmethod
    def show_img(img, window_name) -> None:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, img)
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    def get_image(self, cam, show=True):
        dvr = DvrIntelbras()
        uri = dvr.set_uri(cam)
        try:
            stream = cv2.VideoCapture(uri)
            r, img = stream.read()
        except:
            print("Erro ao acessar o dvr")
            height = 512
            width = 512
            img = np.zeros((height, width, 3), np.uint8)
            img[:] = (0, 124, 255)
        if show:
            self.show_img(img, 'imagem camera')
        return img




#
# dvr = DvrIntelbras()
# # dvr.set_uri(6)
# dvr.get_image(6, True)
