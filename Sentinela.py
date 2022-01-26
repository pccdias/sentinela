import Dvr_Intelbras
from Dvr_Intelbras import *
from configparser import ConfigParser
import cv2
import detector
from detector import *
from datetime import datetime as dt
import base64


#1) varrer uma camera de tempos em tempos. ler quais cameras deverá varrer
#2) capturar a alteração e o objeto com horário
#3) reportar via chatbot

class Sentinela():
    def __init__(self):
        self.t_varredura = 1 #varrer cada camera no intervalo de 1s
        self.dvr = DvrIntelbras()
        parser = ConfigParser()
        parser.read('config_DVR_intelbras.ini')
        aux = parser.sections()
        aux.pop(0)
        # print(aux)
        self.cam_list = []
        for i in aux:
            dic_aux = {}
            dic_aux[i] = parser.get(i,'nome')
            dic_aux['descr'] = parser.get(i,'descr')
            dic_aux['vigiar'] = parser.get(i, 'vigiar')
            self.cam_list.append(dic_aux)
            self.SENSIBILIDADE = .60
        # print(self.cam_list)

    def sentinela_fazendo_ronda(self):
        for cam in self.cam_list:
            # print('cam: ', cam, 'cam[vigiar]: ', cam['vigiar'])
            if cam['vigiar'] == 'True':
                dvr = DvrIntelbras()
                img = dvr.get_image(list(cam.keys())[0], False)

                detector = Detector()

                img_classified, classes_detected = detector.getObjects(img,self.SENSIBILIDADE,0.2,objects=['person', 'car', 'dog'])
                # print(classes_detected)
                # DvrIntelbras.show_img(img_classified,'tagged images returned')
                yield cam , img_classified, classes_detected

    def update_cam_history(self, cam, tag, log_cam):
        # cam = str(cam)
        if cam in log_cam.keys():
            if 'tag1' in log_cam[cam].keys():
                aux = log_cam[cam]['tag1']
                log_cam[cam]['tag0'] = log_cam[cam]['tag1']
                log_cam[cam]['tag1'] = tag
            else:
                log_cam[cam]['tag1'] = tag

        else:
            log_cam[cam] = {'tag0': tag}

        return log_cam

    def sentinela_loop_ronda(self):
        # global flag
        # print('Thread vigiando iniciada...')
        # print("Flag:", flag)
        # sentinela = Sentinela()/
        verify_change = dict()
        log_cam = dict()
        while True:
            # print("flag dentro do while:", flag, id(flag))
            # print(threading.current_thread())
            for cam, img, class_tagged in self.sentinela_fazendo_ronda():
                print(cam, class_tagged)
                if class_tagged:
                    print(log_cam)
                    camera_id = str(list(cam.keys())[0])
                    self.update_cam_history(camera_id, class_tagged, log_cam)
                    print(log_cam)
                    retval, buffer = cv2.imencode('.jpg', img)
                    jpg_as_text = base64.b64encode(buffer)
            yield cam, img, jpg_as_text, class_tagged, log_cam


# sentinela = Sentinela()
# sentinela.sentinela_fazendo_ronda()
# #sentinela.sentinela_loop_ronda()



