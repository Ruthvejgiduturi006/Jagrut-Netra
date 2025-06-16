import cv2
import numpy as np
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import imutils

app = Flask(__name__, static_folder="static")
CORS(app)

# Load OpenCV's pre-trained Haar Cascade model
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Store missing persons database
missing_persons_db = {}

@app.route('/')
def home():
    return render_template("index.html")


### 🟢 1. CROWD MANAGEMENT: Detects and counts faces in an image or video
@app.route('/detect_crowd', methods=['POST'])
def detect_crowd():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['image']
    file_path = "static/uploads/crowd.jpg"
    file.save(file_path)

    # Read the image
    image = cv2.imread(file_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Draw rectangles around faces
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    face_count = len(faces)

    # Save the processed image
    output_path = "static/uploads/crowd_detected.jpg"
    cv2.imwrite(output_path, image)

    return jsonify({"faces_detected": face_count, "image_url": output_path})


### 🟢 2. MISSING PERSONS: Matches a given image with live video
@app.route('/upload_missing', methods=['POST'])
def upload_missing():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['image']
    file_path = "static/uploads/missing_person.jpg"
    file.save(file_path)

    missing_persons_db['person'] = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

    return jsonify({"message": "Missing person image stored"})


@app.route('/detect_missing', methods=['POST'])
def detect_missing():
    if 'frame' not in request.files:
        return jsonify({"error": "No video frame uploaded"}), 400

    file = request.files['frame']
    frame_path = "static/uploads/current_frame.jpg"
    file.save(frame_path)

    # Read the frame
    frame = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)

    if 'person' in missing_persons_db:
        person_img = missing_persons_db['person']

        # Detect faces in the current frame
        faces = face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            person_resized = cv2.resize(person_img, (w, h))

            # Compare faces using Mean Squared Error
            mse = np.mean((face_roi - person_resized) ** 2)
            if mse < 500:
                return jsonify({"alert": "Missing person detected in the crowd!"})

    return jsonify({"message": "No match found"})


### 🟢 3. RESTRICTED AREA SECURITY: Detects any person in a given area
@app.route('/restricted_area', methods=['POST'])
def restricted_area():
    if 'frame' not in request.files:
        return jsonify({"error": "No video frame uploaded"}), 400

    file = request.files['frame']
    frame_path = "static/uploads/restricted_frame.jpg"
    file.save(frame_path)

    # Read the frame
    frame = cv2.imread(frame_path)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        return jsonify({"alert": "Unauthorized person detected in restricted area!"})

    return jsonify({"message": "No unauthorized entry"})


### 🟢 4. NIGHTTIME SECURITY (LIVE MONITORING)
@app.route('/night_security', methods=['POST'])
def night_security():
    if 'frame' not in request.files:
        return jsonify({"error": "No video frame uploaded"}), 400

    file = request.files['frame']
    frame_path = "static/uploads/night_frame.jpg"
    file.save(frame_path)

    # Read the frame
    frame = cv2.imread(frame_path)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        return jsonify({"alert": "Suspicious activity detected at night!"})

    return jsonify({"message": "All clear"})


if __name__ == '__main__':
    os.makedirs("static/uploads", exist_ok=True)
    app.run(debug=True)
