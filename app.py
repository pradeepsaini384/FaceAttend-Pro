import cv2
import os
from flask import Flask,request,render_template
from datetime import date
from datetime import datetime
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib
import mysql.connector
#### Defining Flask App
app = Flask(__name__)

conn = mysql.connector.connect(host = "sql6.freemysqlhosting.net",user = "sql6580072",password ="cYjm5R2g3a",database="sql6580072")
cursor = conn.cursor()
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


#### extract the face from an image
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


################## ROUTING FUNCTIONS #########################

#### Our main page
@app.route('/')
def home():
    names,rolls,times,l = extract_attendance()    
    return render_template('login.html',names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2) 
#
@app.route('/admin')
def admin():
    return render_template('admin_login.html') 
#
@app.route('/adminlog',methods= ['GET','POST'])
def adminlog():
    names,rolls,times,l = extract_attendance()   
    email = request.form.get("email")
    password = request.form.get("password")
    # cid = request.form.get("cid")
    csub = request.form.get("csub")
    trigger = request.form.get("checked")
    print(email,password)
    cursor.execute("""SELECT * FROM `admin` WHERE `email` LIKE '{}' AND `password` LIKE '{}'"""
    .format(email,password))
    admin = cursor.fetchall()

    if len(admin)>0:
        username = admin[0][1]
        users_id = admin[0][0]
        
        names,rolls,times,l = extract_attendance()
        cursor.execute("""SELECT * FROM `live` WHERE `bool` LIKE '1'""")
        livedata=cursor.fetchall()
        print(livedata)
        if (len(livedata)>0):
            print(l)
            return render_template("admin.html",ok=True,livedata=livedata,email=email,password=password,username=username,users_id=users_id,names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2)
        else:
             return render_template("admin.html",email=email,password=password,ok=False,username=username,users_id=users_id,names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2)
 
    else:
        return render_template('admin_login.html')
    # return render_template('admin.html',names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2) 
#
@app.route('/live',methods= ['GET','POST'])
def live():
    names,rolls,times,l = extract_attendance()   
    email = request.form.get("email")
    password = request.form.get("password")
    # cid = request.form.get("cid")
    csub = request.form.get("csub")
    trigger = 1
    cursor.execute("""SELECT * FROM `admin` WHERE `email` LIKE '{}' AND `password` LIKE '{}'"""
    .format(email,password))
    admin = cursor.fetchall()
    if len(admin)>0:
        username = admin[0][1]
        users_id = admin[0][0]
        cursor.execute("""INSERT INTO `live` (`date`,`subject`,`bool`) VALUES
        ('{}','{}','{}')""".format(datetoday,csub,trigger))
        conn.commit()
        cursor.execute("""SELECT * FROM `live` WHERE `bool` LIKE '1'""")
        livedata=cursor.fetchall()
        print(livedata)
        if (len(livedata)>0):
             
            return render_template("admin.html",livedata=livedata,email=email,password=password,ok=False,username=username,users_id=users_id,names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2)
        else:
             return render_template("admin.html",email=email,password=password,ok=False,username=username,users_id=users_id,names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2)
 
        # return render_template("admin.html",email=email,password=password,ok=False,username=username,users_id=users_id,names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2)
@app.route('/add_Data')
def add_Data():
    names,rolls,times,l = extract_attendance()    
    return render_template('add_Data.html',names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2) 

@app.route('/start',methods=['GET','POST'])
def start():
    if 'face_recognition_model.pkl' not in os.listdir('static'):
        return render_template('home.html',totalreg=totalreg(),datetoday2=datetoday2,mess='There is no trained model in the static folder. Please add a new face to continue.') 

    cap = cv2.VideoCapture(0)
    ret = True
    while ret:
        ret,frame = cap.read()
        if extract_faces(frame)!=():
            (x,y,w,h) = extract_faces(frame)[0]
            cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
            face = cv2.resize(frame[y:y+h,x:x+w], (50, 50))
            identified_person = identify_face(face.reshape(1,-1))[0]
            add_attendance(identified_person)
            cv2.putText(frame,f'{identified_person}',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0, 20),2,cv2.LINE_AA)
        cv2.imshow('Attendance',frame)
        if cv2.waitKey(1)==27:
            break
    cap.release()
    cv2.destroyAllWindows()
    names,rolls,times,l = extract_attendance()    
    return render_template('profile.html',names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2) 

#### This function will run when we add a new user
@app.route('/add_Data',methods=['GET','POST'])
def add():
    newusername = request.form['newusername']
    newuserid = request.form['newuserid']
    userimagefolder = 'static/faces/'+newusername+'_'+str(newuserid)
    if not os.path.isdir(userimagefolder):
        os.makedirs(userimagefolder)
    cap = cv2.VideoCapture(0)
    i,j = 0,0
    while 1:
        _,frame = cap.read()
        faces = extract_faces(frame)
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
            cv2.putText(frame,f'Images Captured: {i}/50',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0, 20),2,cv2.LINE_AA)
            if j%10==0:
                name = newusername+'_'+str(i)+'.jpg'
                cv2.imwrite(userimagefolder+'/'+name,frame[y:y+h,x:x+w])
                i+=1
            j+=1
        if j==500:
            break
        cv2.imshow('Adding new User',frame)
        if cv2.waitKey(1)==27:
            break
    cap.release()
    cv2.destroyAllWindows()
    print('Training Model')
    train_model()
    names,rolls,times,l = extract_attendance()    
    return render_template('add_Data.html',names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2) 

@app.route('/add',methods=['GET','POST'])
def addk():
    newusername1 = request.form.get("username")
    newuserid1= request.form.get("user_id")
    newusername = str(newusername1)
    newuserid = str(newuserid1)
    
    cursor.execute("""SELECT * FROM `users` WHERE `user_id` LIKE '{}' """
    .format(newuserid))
    myuser = cursor.fetchall()
    print(myuser)
    userimagefolder = 'static/faces/'+newusername+'_'+newuserid
    if not os.path.isdir(userimagefolder):
        os.makedirs(userimagefolder)
    cap = cv2.VideoCapture(0)
    i,j = 0,0
    while 1:
        _,frame = cap.read()
        faces = extract_faces(frame)
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
            cv2.putText(frame,f'Images Captured: {i}/50',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0, 20),2,cv2.LINE_AA)
            if j%10==0:
                name = newusername+'_'+str(i)+'.jpg'
                cv2.imwrite(userimagefolder+'/'+name,frame[y:y+h,x:x+w])
                i+=1
            j+=1
        if j==500:
            break
        cv2.imshow('Adding new User',frame)
        if cv2.waitKey(1)==27:
            break
    cap.release()
    cv2.destroyAllWindows()
    print('Training Model')
    train_model()
    names,rolls,times,l = extract_attendance()    
    return render_template('add_Data.html',names=names,rolls=rolls,times=times,l=l,totalreg=totalreg(),datetoday2=datetoday2) 

@app.route('/validation',methods=['GET','POST'])
def validation():
    email = request.form.get("email")
    password = request.form.get("password")
    # csub = request.form.get("csub")
    # cname = request.form.get("cname")
    print(email,password)
    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'"""
    .format(email,password))
    users = cursor.fetchall()
    username = users[0][1]
    print(username)
        
    users_id = users[0][0]
    print(users_id)
    print(type(users_id))
        
    if len(users)>0:
        
        userimagefolder = 'static/faces/'+username+'_'+users_id
        
        cursor.execute("""SELECT * FROM `live` WHERE `bool` LIKE '1'""")
        livedata=cursor.fetchall()
        print(livedata)

        if (len(livedata)>0):  
               return render_template('profile.html',livedata=livedata,email=email,password=password,username=username,users_id=users_id)
        # if os.path.isdir(userimagefolder):
        #     error = "! Face Data Already Exist !"
            
                
        #     return render_template('profile.html',email=email,password=password,username=username,error=error,users_id=users_id)

        # else:
        #     print("else")
        #     return render_template('profile.html',email=email,password=password,username=username,users_id=users_id)
            
    else:
        return render_template('login.html')
# @app.route('/registration')
# def registration():
#     return render_template('registration.html')

@app.route('/registration',methods=['GET','POST'])
def registration():
    rollno = request.form.get("rollno")
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("pwd")
    print(rollno,name,email,password)
    cursor.execute("""INSERT INTO `users` (`user_id`,`name`,`email`,`password`) VALUES
    ('{}','{}','{}','{}')""".format(rollno,name,email,password))
    conn.commit()
    
    cursor.execute("""SELECT * FROM `users` WHERE `user_id` LIKE '{}' """
    .format(rollno))
    myuser = cursor.fetchall()
    print(myuser)
    if len(myuser)>0:
         error="Registration succesfully ! "
         return render_template('registration.html',error=error)
        
    else:        
         return render_template('registration.html')

@app.route('/logout',methods=['GET'])
def logout():

    render_template('login.html')
        
#### Our main function which runs the Flask App
if __name__ == '__main__':
    app.run(debug=True)