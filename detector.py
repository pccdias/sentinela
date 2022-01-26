import cv2
from Dvr_Intelbras import *
import datetime as datetime
import time

class Detector():

    def __init__(self):
        self.classNames = []
        self.classFile = "coco.names"
        with open(self.classFile,"rt") as f:
            self.classNames = f.read().rstrip("\n").split("\n")

        self.configPath = "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
        self.weightsPath = "frozen_inference_graph.pb"

        self.net = cv2.dnn_DetectionModel(self.weightsPath,self.configPath)
        self.net.setInputSize(320,320)
        self.net.setInputScale(1.0/ 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)
        self.SENSIBILIDADE = .80


    def save_files(img,tagged_img):
        
        if img is not None:
            filename= f'./img_tagged/original/img{time.strftime("%Y_%m_%d_%H_%M_%S")}.png'
            cv2.imwrite(filename, img)
        if tagged_img is not None:
            filename= f'./img_tagged/tagged_img{time.strftime("%Y_%m_%d_%H_%M_%S")}.png'
            cv2.imwrite(filename, tagged_img)


    def getObjects(self, img, thres, nms, draw=True, objects=[]):
        classIds, confs, bbox = self.net.detect(img,confThreshold=thres,nmsThreshold=nms)
        #print(classIds,bbox)
        if len(objects) == 0: objects = self.classNames
        objectInfo =[]
        detected_classes = []
        if len(classIds) != 0:
            for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
                className = self.classNames[classId - 1]
                if className in objects:
                    detected_classes.append(className)
                    objectInfo.append([box,className])
                    if (draw):
                        cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                        cv2.putText(img,self.classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                        cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                        cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                        cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
        detected_classes.sort()
        #save_file(None,img)
        
        return img,detected_classes


    

    def main(self):


        dvr = DvrIntelbras()
        uri = dvr.set_uri(8)


        cap = cv2.VideoCapture(uri)
        cap.set(3,640)
        cap.set(4,480)
        #cap.set(10,70)


        while True:
            time.sleep(1)
            success, img = cap.read()
            result, objectInfo = detector.getObjects(img,self.SENSIBILIDADE,0.2,objects=['person', 'car', 'dog'])
            print(objectInfo)
            filename= f'./img_tagged/tagged_img{time.strftime("%Y_%m_%d_%H_%M_%S")}.png'
            if objectInfo is not None:
                cv2.imwrite(filename, img)
            else:
                print("Nada Detectado")
            cv2.waitKey(1)



if __name__ == "__main__":
    detector = Detector()
    detector.main()


