
import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'databaseURL': "https://face-detection-for-attendance-default-rtdb.firebaseio.com/",
                                    'storageBucket': "face-detection-for-attendance.appspot.com"})

bucket = storage.bucket()


bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images into a list
folderModePath = 'Resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Load the encoding file
print("Loading Encode File ...")
file = open('Encodefiles.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[130:130+480, 20:20+640] = img
    imgBackground[44:44+620, 808:808+400] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                 y1, x2, y2, x1 = faceLoc
                 y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                 bbox = 20+x1, 130+y1, x2-x1, y2-y1
                 imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                 id = studentIds[matchIndex]
                 if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(10)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # Get the Data
                studentInfo = db.reference(f'students/{id}').get()
                print(studentInfo)
                # Get the Image from the storage
                blob = bucket.get_blob(f'image/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last attendance time'].strip(), "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'students/{id}')
                    studentInfo['total attendance'] += 1
                    ref.child('total attendance').set(studentInfo['total attendance'])
                    ref.child('last attendance time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 1
                    cv2.waitKey(10)
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                
                

                if counter <= 10:
                   cv2.putText(imgBackground, str(studentInfo['total attendance']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1.0,
                        (0, 0, 0), 1)
           # cv2.putText(imgbackground, str(studentInfo['name']), (900, 430), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0), 1)
                   (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                   offset = (414 - w) // 2
                   cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1.0,
                        (0, 0, 0), 1)
                cv2.putText(imgBackground, str(studentInfo['major']), (1000, 520), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                        (0, 0, 0), 1)
                cv2.putText(imgBackground, str(id), (1006, 470), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)
                cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                        (0, 0, 0), 1)
                cv2.putText(imgBackground, str(studentInfo['year']), (850, 625), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)
                cv2.putText(imgBackground, str(studentInfo['starting year']), (1050, 625), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                        (0, 0, 0), 1)
                imgBackground[175:175+216, 909:909+216] = imgStudent
                counter += 1
                

                   

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 620, 808:808 + 400] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)


