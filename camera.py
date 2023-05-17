import cv2
import os

from datetime import date
from datetime import datetime

import pandas as pd
import joblib

class Video(object):
    def __init__(self):
        self.cap=cv2.VideoCapture(0)
        self.faceDetect=cv2.CascadeClassifier('static/haarcascade_frontalface_default.xml')
        self.face_detector = cv2.CascadeClassifier('static/haarcascade_frontalface_default.xml')
        self.datetoday = date.today().strftime("%m_%d_%y")
        self.datetoday2 = date.today().strftime("%d-%B-%Y")
    def extract_faces(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = self.face_detector.detectMultiScale(gray, 1.3, 5)
        return face_points
    def identify_face(self,facearray):
        model = joblib.load('static/face_recognition_model.pkl')
        return model.predict(facearray)
    def extract_attendance(self):
        df = pd.read_csv(f'Attendance/Attendance-{self.datetoday}.csv')
        names = df['Name']
        rolls = df['Roll']
        times = df['Time']
        l = len(df)
        return names,rolls,times,l
    def start(self):
        p = 0
        # cap = cv2.VideoCapture(0)
        ret = True
        while ret:
            ret,frame = self.cap.read()
            if self.extract_faces(frame)!=():
                (x,y,w,h) = self.extract_faces(frame)[0]
                cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
                face = cv2.resize(frame[y:y+h,x:x+w], (50, 50))
                identified_person = self.identify_face(face.reshape(1,-1))[0]
                print(identified_person)
                self.add_attendance(identified_person)
                cv2.putText(frame,f'{identified_person}',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0, 20),2,cv2.LINE_AA)
            # cv2.imshow('Attendance',frame)
                # self.add_attendance(identified_person)
            if cv2.waitKey(20) & 0xF==27:
                break
            # p+=1
            # print(p)
            ret,jpg=cv2.imencode('.jpg',frame)
            return jpg.tobytes()
        
    def releasse(self):
        self.cap.release()
        cv2.destroyAllWindows()
    
    def add_attendance(self,name):
        username = name.split('_')[0]
        userid = name.split('_')[1]
        current_time = datetime.now().strftime("%H:%M:%S")
        
        df = pd.read_csv(f'Attendance/Attendance-{self.datetoday}.csv')
        if int(userid) not in list(df['Roll']):
            with open(f'Attendance/Attendance-{self.datetoday}.csv','a') as f:
                f.write(f'\n{username},{userid},{current_time}')

   

