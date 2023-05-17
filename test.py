# # from app import train_model

# # print(train_model())



# # user = ''
# # id = 0

# # def check():
# #     global user,id
# #     user= user+'pradeep'
# #     id = id+10
# #     return 0
# # check()
# # print(user)
# # print(id)# import required libraries
# import cv2

# # read the input image
# img = cv2.imread('/static/images/hacker.png')

# # convert to grayscale of each frames
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# # read the haarcascade to detect the faces in an image
# face_cascade = cv2.CascadeClassifier('haarcascades\haarcascade_frontalface_default.xml')

# # detects faces in the input image
# faces = face_cascade.detectMultiScale(gray, 1.3, 4)
# print('Number of detected faces:', len(faces))

# # loop over all detected faces
# if len(faces) > 0:
#    for i, (x, y, w, h) in enumerate(faces):
 
#       # To draw a rectangle in a face
#       cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
#       face = img[y:y + h, x:x + w]
#       cv2.imshow("Cropped Face", face)
#       cv2.imwrite(f'face{i}.jpg', face)
#       print(f"face{i}.jpg is saved")
 
# # display the image with detected faces
# cv2.imshow("image", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

from multiprocessing import Pool, Queue
import time
import cv2

# intialize global variables for the pool processes:
def init_pool(d_b):
    global detection_buffer
    detection_buffer = d_b


def detect_object(frame):
    time.sleep(1)
    detection_buffer.put(frame)


def show():
    while True:
        print("show")
        frame = detection_buffer.get()
        if frame is not None:
            cv2.imshow("Video", frame)
        else:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    return


# required for Windows:
if __name__ == "__main__":

    detection_buffer = Queue()
    # 6 workers: 1 for the show task and 5 to process frames:
    pool = Pool(6, initializer=init_pool, initargs=(detection_buffer,))
    # run the "show" task:
    show_future = pool.apply_async(show)

    cap = cv2.VideoCapture(0)

    futures = []
    while True:
        ret, frame = cap.read()
        if ret:
            f = pool.apply_async(detect_object, args=(frame,))
            futures.append(f)
            time.sleep(0.025)
        else:
            break
    # wait for all the frame-putting tasks to complete:
    for f in futures:
        f.get()
    # signal the "show" task to end by placing None in the queue
    detection_buffer.put(None)
    show_future.get()
    print("program ended")