import cv2
import os
from flask import Flask,request,render_template,Response,url_for, flash, send_file,redirect
from datetime import date
from datetime import datetime
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib

from flask_mail import Mail, Message

#### this are importing from diffrent python files which is made in this project
from sqlCon import cursor,authentication,authentication_for_admin,conn,live_gen,registration
from camera import Video
from face import Video1


import time

#### Defining Flask App
app = Flask(__name__)


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mca22.pradeep.saini@sunstone.edu.in' # replace with your email address
app.config['MAIL_PASSWORD'] = 'sunstone304785' # replace with your email password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


#### global declaration of username or userid for make useable in all functions
username = ''
users_id = ''

#### Saving Date today in 2 different formats
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")


#### Initializing VideoCapture object to access WebCam
face_detector = cv2.CascadeClassifier('static/haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)


#### If these directories don't exist, create them
if not os.path.isdir('Attendance'):
    os.makedirs('Attendance')
if not os.path.isdir('static/faces'):
    os.makedirs('static/faces')
if f'Attendance-{datetoday}.csv' not in os.listdir('Attendance'):
    with open(f'Attendance/Attendance-{datetoday}.csv','w') as f:
        f.write('Name,Roll,Time')


#### get a number of total registered users
def totalreg():
    return len(os.listdir('static/faces'))


##### extract the face from an image
def extract_faces(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_points = face_detector.detectMultiScale(gray, 1.3, 5)
    return face_points


#### Identify face using ML model
def identify_face(facearray):
    model = joblib.load('static/face_recognition_model.pkl')
    return model.predict(facearray)


#### A function which trains the model on all the faces available in faces folder
def train_model():
    faces = []
    labels = []
    userlist = os.listdir('static/faces')
    for user in userlist:
        for imgname in os.listdir(f'static/faces/{user}'):
            img = cv2.imread(f'static/faces/{user}/{imgname}')
            resized_face = cv2.resize(img, (50, 50))
            faces.append(resized_face.ravel())
            labels.append(user)
    faces = np.array(faces)
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(faces,labels)
    joblib.dump(knn,'static/face_recognition_model.pkl')
    print('hanbhai done')

    return 'han bhai done'


#### Extract info from today's attendance file in attendance folder
def extract_attendance():
    df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
    names = df['Name']
    rolls = df['Roll']
    times = df['Time']
    l = len(df)
    return names,rolls,times,l


#### Add Attendance of a specific user
def add_attendance(name):
    username = name.split('_')[0]
    userid = name.split('_')[1]
    current_time = datetime.now().strftime("%H:%M:%S")
    
    df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
    if int(userid) not in list(df['Roll']):
        with open(f'Attendance/Attendance-{datetoday}.csv','a') as f:
            f.write(f'\n{username},{userid},{current_time}')
# def sql_connect(email,password):
    
def gen(camera):
    #this will send images to web for give attendence
    while True:
        frame=camera.start()
        yield(b'--frame\r\n'
       b'Content-Type:  image/jpeg\r\n\r\n' + frame +
         b'\r\n\r\n')
def gen1(face):
#this will send images to web for train model
    while True:
        frame=face.start()
        yield(b'--frame\r\n'
       b'Content-Type:  image/jpeg\r\n\r\n' + frame +
         b'\r\n\r\n')


#routing functions start 
@app.route('/')
#for home page
def home():
    names,rolls,times,l = extract_attendance()   
    return render_template('login.html',names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2) 



@app.route('/validation')
#this is only face detaction model calling function for give attendence
def video():    
    return Response(gen(Video()),
    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/face')
#this is only face detaction model calling function for train face model
def video1():
    global username,users_id
    return Response(gen(Video1(username,users_id)),
    mimetype='multipart/x-mixed-replace; boundary=frame')
#this is face method call which did nothing but it remove the error of uppar /face method
@app.route('/face',methods=['GET','POST'])
def face():
    newusername1 = request.form.get("username")
    newuserid1= request.form.get("user_id")
    newusername = str(newusername1)
    newuserid = str(newuserid1)
    print(newuserid)
    print(newusername)
    return render_template('face.html',username=newusername,user_id=newuserid)
#this is for call or train_model function
@app.route('/train')
def train():
    train_model()
    print('called')
    time.sleep(2)
    return Response('ok')

#for admin log in 
@app.route('/admin')
def admin():
    return render_template ('admin.html')

#login admin panel 
@app.route('/adminlog',methods=['GET','POST'])
def adminlog():
    email = request.form.get("email")
    password = request.form.get("password")
    # print(email,password)
    admin = authentication_for_admin(email,password)
    if len(admin)>0:
        username = admin[0][1]
        users_id = admin[0][0]
        
        names,rolls,times,l = extract_attendance()
        cursor.execute("""SELECT * FROM `live` WHERE `bool` LIKE '1'""")
        livedata=cursor.fetchall()
        print(livedata)
        if (len(livedata)>0):
            # print(l)
            return render_template("adminlog.html",ok=True,livedata=livedata,email=email,password=password,username=username,users_id=users_id,names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2)
        else:
             return render_template("adminlog.html",email=email,password=password,ok=False,username=username,users_id=users_id,names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2)
 
    else:
        return render_template('admin.html')
#for Live Genereted attendence
@app.route('/live',methods= ['GET','POST'])
def live():
    names,rolls,times,l = extract_attendance()
    csub = request.form.get("csub")
    deadline = request.form.get("deadline")
    checked = 1
    # print(csub,deadline)
    if(csub!=None):
        live_gen(deadline,csub,checked)
        cursor.execute("""SELECT * FROM `live` WHERE `bool` LIKE '1'""")
        livedata=cursor.fetchall()
            # print(livedata)
        return render_template("adminlog.html",livedata=livedata,ok=True,names=names,rolls=rolls,times=times,l=l)
    else:
        return render_template('admin.html')
   
 
#For registration page 
@app.route('/register')
def register():
    return render_template('signup.html')
#for storing sign up data 
@app.route('/signup',methods=['GET','POST'])
def signup():
    name = request.form.get("name")
    rollno = request.form.get("rollno")
    email = request.form.get("email")
    password = request.form.get("password")
    # print(rollno,name,email,password)
    if(name!=None):            
        myuser = registration(rollno,name,email,password)
        cursor.execute("""SELECT * FROM `live` WHERE `bool` LIKE '1'""")
        livedata=cursor.fetchall()
        if len(myuser)>0:
            return render_template('home1.html',livedata=livedata,valid=False,)
            
        else:        
            return render_template('signup.html',error=True)
    else:
        return render_template('signup.html',error=True)

#this is login validation method which match data according to sql 
@app.route('/validation',methods=['GET','POST'])
def validation():
    email = request.form.get("email")
    password = request.form.get("password")
    # print(email,password)
    if(email!=None):
        users = authentication(email,password)
        if(len(users)>0):
            global username,users_id
            # print(users)
            username = users[0][1]
            # app.config['username1']=username
            # print(username)
                
            users_id = users[0][0]
            # print(users_id)
            # print(type(users_id))

            cursor.execute("""SELECT * FROM `live` WHERE `bool` LIKE '1'""")
            
            livedata=cursor.fetchall()
            # print(livedata)
            
            
            return render_template('home12.html',username=username,users_id=users_id,livedata=livedata,valid=False)
        else:
            return render_template('login.html',f=True)
    else:
        return render_template('login.html',f=True)
    


@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        email_to = request.form['email_to']
        email_subject = f"Attendece Of The Date : {datetoday}"
        email_body = "Please Find the attachment"
        
        # create message object
        msg = Message(subject=email_subject, sender='mca22.pradeep.saini@sunstone.edu.in', recipients=[email_to])
        
        # attach CSV file to message
        csv_file_path = f'Attendance/Attendance-{datetoday}.csv' # replace with path to your CSV file
        with app.open_resource(csv_file_path) as csv_file:
            msg.attach('csv_file.csv', 'text/csv', csv_file.read())
        
        # add body to message
        msg.body = email_body
        
        # send message
        mail.send(msg)
        
        # return redirect(url_for('send_email'))
        return "successfull"
    
    return "failed"

@app.route('/issue',methods=['GET','POST'])
def issue():
    if request.method == 'POST':
        email_to = request.form['email']
        message = request.form['comment']

        email_subject = f"Issue Or Inquery "
        email_body = "Thanks For Contacting US \n Your Issue is : \n"+message
        msg = Message(subject=email_subject, sender='mca22.pradeep.saini@sunstone.edu.in', recipients=[email_to])
        # add body to message
        msg.body = email_body
        
        # send message
        mail.send(msg)
        return "done"
#### Our main function which runs the Flask App
if __name__ == '__main__':
    app.run(debug=True)