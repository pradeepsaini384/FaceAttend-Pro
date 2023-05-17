import mysql.connector

conn = mysql.connector.connect(host = "localhost",user= "root",password ="",database="attendence")
# conn = mysql.connector.connect(host = "sql12.freesqldatabase.com",user= "sql12619075",password ="yRRNa1dzQp",database="sql12619075")
cursor = conn.cursor()
def authentication(email,password):
    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email,password))
    users = cursor.fetchall()
    return users
def authentication_for_admin(email,password):
    cursor.execute("""SELECT * FROM `admin` WHERE `email` LIKE '{}' AND `password` LIKE '{}'"""
    .format(email,password))
    admin = cursor.fetchall()
    return admin
def live_gen(datetoday,csub,trigger):
    cursor.execute("""INSERT INTO `live` (`date`,`subject`,`bool`) VALUES  ('{}','{}','{}')""".format(datetoday,csub,trigger))
    conn.commit()
def registration(rollno,name,email,password):
    cursor.execute("""INSERT INTO `users` (`user_id`,`name`,`email`,`password`) VALUES ('{}','{}','{}','{}')""".format(rollno,name,email,password))
    conn.commit()
    cursor.execute("""SELECT * FROM `users` WHERE `user_id` LIKE '{}' """.format(rollno))
    myuser = cursor.fetchall()
    return myuser