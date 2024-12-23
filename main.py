# -*- coding: utf-8 -*-
# Time : 2024/11/15 23:38
# Author : lirunsheng
# User : l'r's
# Software: PyCharm
# File : main_fuits.py
import copy
import time

from PyQt5 import QtWidgets, QtCore, QtGui
from untitled_cat import Ui_MainWindow
import sys
import base64
import datetime
import threading
import pymysql

from image import *
from test_face import *
from mysql_operation import *
from PH_711 import *
from sg90 import ServoMotor

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.img = None
        self.weight = 0
        self.all_money = []
        self.category = 'None'
        self.category_weight = 0
        self.flage = 0
        self.lebel = False
        self.Detecting_cats = True
        self.Detecting_face = False
        self.weight_last = 0
        self.face_time = time.time()
        self.weight_add_flag = True
        self.add_flag = True
        self.Detecting_face_count = 0
        self.img1 = None
        self.xg = False
        self.xg_name = None
        self.xg_time = None
        self.xg_weight = None
        self.xg_location = None

        face_cascade_path = '/home/pi/project/catface-master/data/haarcascades/haarcascade_frontalcatface_extended.xml'
        photos_path = '/home/pi/project/catface-master/data/photos'
        self.comparer = ImageComparer(photos_path, face_cascade_path)

        self.app = QtWidgets.QApplication([])
        self.setupUi(self)
        self.cap = cv2.VideoCapture(0)  # 0表示默认摄像头
        #self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))


        # 连接数据库
        db = Database(host="120.25.173.40", user="root", password="root_123R", database="face_cat")
        # 创建Cat和CatFood对象
        self.cat = Cat(db)
        self.cat_food = CatFood(db)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.receiveFrame)
        self.timer.setInterval(1)
        self.timer.start()

        model_pb_path = "v5lite-cat.onnx"
        so = ort.SessionOptions()
        self.net = ort.InferenceSession(model_pb_path, so)

        self.send = Hx711()
        self.send.setup()

        self.servo_pin = 40  # 根据实际情况设置引脚
        self.servo = ServoMotor(self.servo_pin)
    #
    # def get_weight(self):
    #     self.weight_last = self.send.weight
    #     while True:
    #         self.send.start()
    #         if self.send.weight >200:
    #             break
    #
    #
    def add_cat(self, img, label):
        self.add_flag = False
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        name_jpg = current_time + '_' + label + '.jpg'
        path = os.path.join('/home/pi/project/catface-master/recognition_result', name_jpg)
        img = cv2.resize(img, [320, 320], interpolation=cv2.INTER_AREA)
        cv2.imwrite(path, img)
        # 打开图像文件
        with open(path, 'rb') as f:
            # 读取图像文件内容
            image_data = f.read()
            # 将图像数据编码为base64字符串
            base64_str = base64.b64encode(image_data)
        # image = base64.b64encode(img)
        self.send.weight
        self.send.start()
        self.weight_last = self.send.weight
        while True:
            self.send.start()
            self.servo.set_angle(90)
            time.sleep(1)
            if self.send.weight > 200:
                break
        # 添加一只猫
        # print(label)
        self.cat.add(name=label, time=current_time, weight=self.send.weight-self.weight_last, image_data=base64_str)
        print(self.send.weight-self.weight_last)
        self.add_flag = True
        self.xg = True
        self.xg_name = label
        self.xg_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.xg_weight = str(self.send.weight-self.weight_last)
        self.xg_location = ''


    def receiveFrame(self):
        ret, img = self.cap.read()
        self.flage += 1

        if self.Detecting_cats and self.flage > 10:
            img0 = copy.copy(img)
            flag_face = image_detection(img0, self.net)
            self.flage = 0
            if flag_face:
                self.Detecting_face = True
                self.Detecting_cats = False
            # print(self.lebel)
        elif self.Detecting_face and self.comparer.run_flage:
            self.img1 = copy.copy(img)
            self.Detecting_face_count += 1
            recognition_thread = threading.Thread(target=self.comparer.run_face, args=(self.img1,))
            recognition_thread.start()
            # print(label)
        if self.Detecting_face_count == 80:
            self.comparer.detection_name = 'other'
        if self.comparer.detection_name is not None and self.add_flag:
            self.Detecting_face_count = 0
            self.Detecting_face = False
            self.face_time = time.time()
            # self.add_cat(img1, self.comparer.detection_name)
            rec_thread = threading.Thread(target=self.add_cat, args=(self.img1, self.comparer.detection_name))
            rec_thread.start()
            self.comparer.detection_name = None
        if self.xg:
            self.xg = False
            self.textEdit_name.setText(self.xg_name)
            self.textEdit_time.setText(self.xg_time)
            self.textEdit_weight.setText(self.xg_weight)
            self.textEdit_location.setText(self.xg_location)
        if int(time.time() - self.face_time) > 200:
            self.Detecting_face = False
            self.Detecting_cats = True
            self.face_time = time.time()
        img = cv2.resize(img, [320, 320], interpolation=cv2.INTER_AREA)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888)
        self.frame.setPixmap(QtGui.QPixmap.fromImage(img))
        self.frame.setScaledContents(True)

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)  # 解决实际和预览大小不一样的问题
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
