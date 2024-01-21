import cv2
import face_recognition
import pickle
import os


import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{'databaseURL':"https://face-detection-for-attendance-default-rtdb.firebaseio.com/",
'storageBucket':"face-detection-for-attendance.appspot.com"})



# Specify the directory containing the images
ImagesPath = 'image'
PathList = os.listdir(ImagesPath)
ImageList = []
student_id = []

# Load images and extract student IDs from filenames
for path in PathList:
    ImageList.append(cv2.imread(os.path.join(ImagesPath, path)))
    student_id.append(os.path.splitext(path)[0])
    filename=f'{ImagesPath}/{path}'  #run this code again in case of malfun
    bucket=storage.bucket()
    blob=bucket.blob(filename)
    blob.upload_from_filename(filename)

def findingEncoding(ImageList):
    encodelist = []
    for i, img in enumerate(ImageList):
        # Convert image to RGB format (required by face_recognition library)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Extract face encodings for all faces in the image
        face_encodings = face_recognition.face_encodings(img)
        
        # Check if any face is detected
        if face_encodings:
            # Append only the first face encoding
            encodelist.append(face_encodings[0])
        else:
            # Handle the case when no face is detected
            print(f"No face detected in {PathList[i]}")
        
    return encodelist

print("Encoding started...")
encodelistknown = findingEncoding(ImageList)
encoding_list_id = [encodelistknown, student_id]
print("Encoding completed.")

# Save face encodings and corresponding student IDs to a binary file
file = open("Encodefiles.p", 'wb')
pickle.dump(encoding_list_id, file)
file.close()
print("Binary file saved")
