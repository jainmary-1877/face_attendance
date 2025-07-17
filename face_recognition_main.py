import face_recognition
import cv2
import csv
import os
import numpy as np
from datetime import datetime

# Path to your known faces
path = 'faces'
images = []
names = []

# Load images
for filename in os.listdir(path):
    img = cv2.imread(f'{path}/{filename}')
    images.append(img)
    names.append(os.path.splitext(filename)[0])

# Encode known faces
def find_encodings(images):
    encodings = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        enc = face_recognition.face_encodings(img)
        if enc:
            encodings.append(enc[0])
    return encodings

known_encodings = find_encodings(images)

# Attendance function
def mark_attendance(name):
    date_today = datetime.now().date()

    # Read existing records
    try:
        with open('Attendance.csv', 'r') as f:
            reader = csv.reader(f)
            attendance_data = list(reader)
    except FileNotFoundError:
        attendance_data = []

    # Check if already marked today
    already_marked = False
    for row in attendance_data:
        if len(row) >= 2 and row[0] == name and row[1] == str(date_today):
            already_marked = True
            break

    if not already_marked:
        now = datetime.now()
        time_string = now.strftime('%H:%M:%S')
        date_string = now.strftime('%Y-%m-%d')
        with open('Attendance.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([name, date_string, time_string])
        print(f"✅ Marked attendance for {name} at {time_string}")
    else:
        print(f"🟡 {name} already marked for {date_today}")
# Webcam
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    faces_cur_frame = face_recognition.face_locations(rgb_small)
    encodings_cur_frame = face_recognition.face_encodings(rgb_small, faces_cur_frame)

    for encodeFace, faceLoc in zip(encodings_cur_frame, faces_cur_frame):
        matches = face_recognition.compare_faces(known_encodings, encodeFace)
        face_dis = face_recognition.face_distance(known_encodings, encodeFace)
        matchIndex = np.argmin(face_dis)

        if matches[matchIndex]:
            name = names[matchIndex].capitalize()
            y1, x2, y2, x1 = [v*4 for v in faceLoc]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, name, (x1+6, y2-6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            mark_attendance(name)

    cv2.imshow('Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
