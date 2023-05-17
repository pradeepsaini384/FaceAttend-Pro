import cv2
import os
import time
from datetime import date
import joblib

class Video1(object):
    def __init__(self,username,users_id):
        self.cap=cv2.VideoCapture(0)
        # self.faceDetect=cv2.CascadeClassifier('static/haarcascade_frontalface_default.xml')
        self.face_detector = cv2.CascadeClassifier('static/haarcascade_frontalface_default.xml')
        self.datetoday = date.today().strftime("%m_%d_%y")
        self.datetoday2 = date.today().strftime("%d-%B-%Y")
        self.username = str(username)
        # print("type",type(self.username))
        self.users_id=str(users_id)
    def extract_faces(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = self.face_detector.detectMultiScale(gray, 1.3, 5)
        return face_points
    def identify_face(self,facearray):
        model = joblib.load('static/face_recognition_model.pkl')
        return model.predict(facearray)
    def start(self):
        userimagefolder = 'static/faces/'+self.username+'_'+self.users_id
        if not os.path.isdir(userimagefolder):
            os.makedirs(userimagefolder)
        i,j,k = 0,0,0
        while 1:
            _,frame = self.cap.read()
            faces = self.extract_faces(frame)
            
            for (x,y,w,h) in faces:
                while(j<21):
                    cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
                    
                    cv2.putText(frame,f'Images Capturing Done..........',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0, 20),2,cv2.LINE_AA)
                    name = self.username+'_'+str(j)+'.jpg'
                    
                    cv2.imwrite(userimagefolder+'/'+name,frame[y:y+h,x:x+w])
                    i+=1
                    j+=1
                    
                
            
            # cv2.imshow('Adding new User',frame)
            # if cv2.waitKey(20) & 0xF==27:
            #     break
            ret,jpg=cv2.imencode('.jpg',frame)
            # if j==20:
            #     break

            return jpg.tobytes()
            
    def release(self):
            self.cap.release()
            cv2.destroyAllWindows()