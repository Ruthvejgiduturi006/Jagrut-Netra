import cv2
import streamlit as st
import numpy as np
import os
import time
import math
import winsound
from collections import defaultdict

# Sound configuration
ALERT_FREQ = 2000  # Hz
ALERT_DUR = 1000   # milliseconds
ALERT_COOLDOWN = 5  # seconds

# Streamlit Page Configuration
st.set_page_config(
    page_title="Jagrut Netra",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS Styling
st.markdown(
    """
    <style>
        body {
            font-family: 'Open Sans', sans-serif;
            color: #fff;
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: url('https://theintercept.com/wp-content/uploads/2020/01/3atkinson70a-1579897004.gif?fit=1000%2C500') no-repeat center center/cover;
        }
        .title {
            font-size: 45px;
            font-weight: bold;
            text-align: center;
            color: #ffffff;
            text-shadow: 3px 3px 10px black;
            margin-top: 20px;
            position: relative;
        }
        .stButton button {
            background: rgba(0, 0, 0, 0.5) !important;
            color: #ffffff !important;
            border: 2px solid white !important;
            border-radius: 50px !important;
            padding: 15px 40px !important;
            font-size: 1.2em !important;
            font-family: 'Open Sans', sans-serif !important;
            cursor: pointer;
            transition: background-color 0.3s, color 0.3s;
            position: relative;
        }
        .stButton button:hover {
            background-color: white !important;
            color: black !important;
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            padding: 20px;
        }
        .grid-item {
            padding: 15px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            text-align: center;
        }
        .stApp {
            background: transparent !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown('<p class="title">JAGRUT NETRA 🧿🔍</p>', unsafe_allow_html=True)

# Section Buttons
col1, col2, col3, col4, col5 = st.columns(5)
with st.container():
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)

    with col1:
        st.markdown('<div class="grid-item">', unsafe_allow_html=True)
        section1 = st.button("Crowd Management")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="grid-item">', unsafe_allow_html=True)
        section2 = st.button("Fire & Smoke Detection")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="grid-item">', unsafe_allow_html=True)
        section3 = st.button("Restricted Area Security")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="grid-item">', unsafe_allow_html=True)
        section4 = st.button("Night Time Security")
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="grid-item">', unsafe_allow_html=True)
        section5 = st.button("Loitering Detection")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Section Detection
selected_section = None
if section1: selected_section = "Crowd Management"
if section2: selected_section = "Fire & Smoke Detection"
if section3: selected_section = "Restricted Area Security"
if section4: selected_section = "Night Time Security"
if section5: selected_section = "Loitering Detection"

# Models
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class AlertSystem:
    def __init__(self):
        self.last_alert = 0
        
    def trigger(self):
        if time.time() - self.last_alert > ALERT_COOLDOWN:
            try:
                winsound.Beep(ALERT_FREQ, ALERT_DUR)
            except:
                os.system('afplay /System/Library/Sounds/Ping.aiff')  # macOS fallback
            self.last_alert = time.time()

# Fire & Smoke Detection
def detect_fire_smoke():
    alert = AlertSystem()
    cap = cv2.VideoCapture(0)
    stframe = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to capture video.")
            break

        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_fire = np.array([18, 50, 50])
        upper_fire = np.array([35, 255, 255])
        lower_smoke = np.array([0, 0, 100])
        upper_smoke = np.array([180, 50, 255])

        fire_mask = cv2.inRange(hsv, lower_fire, upper_fire)
        smoke_mask = cv2.inRange(hsv, lower_smoke, upper_smoke)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel)
        smoke_mask = cv2.morphologyEx(smoke_mask, cv2.MORPH_OPEN, kernel)

        fire_detected = False
        contours_fire, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_fire:
            if cv2.contourArea(cnt) > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "Fire Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                fire_detected = True

        smoke_detected = False
        contours_smoke, _ = cv2.findContours(smoke_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_smoke:
            if cv2.contourArea(cnt) > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (200, 200, 200), 2)
                cv2.putText(frame, "Smoke Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
                smoke_detected = True

        if fire_detected or smoke_detected:
            alert.trigger()

        _, jpeg = cv2.imencode('.jpg', frame)
        stframe.image(jpeg.tobytes(), channels="BGR", use_column_width=True)

    cap.release()
    cv2.destroyAllWindows()

# Loitering Detection
def detect_loitering():
    alert = AlertSystem()
    cap = cv2.VideoCapture(0)
    stframe = st.empty()
    fgbg = cv2.createBackgroundSubtractorMOG2()
    min_contour_area = 500
    loiter_threshold = 5  # seconds
    objects = defaultdict(lambda: {'first_seen': None, 'positions': []})

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to access camera.")
            break

        frame = cv2.resize(frame, (640, 480))
        mask = fgbg.apply(frame)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        current_time = time.time()
        alert_triggered = False

        for cnt in contours:
            if cv2.contourArea(cnt) < min_contour_area:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            cx, cy = x + w//2, y + h//2
            obj_id = f"{cx}_{cy}"

            if not objects[obj_id]['first_seen']:
                objects[obj_id]['first_seen'] = current_time
                
            objects[obj_id]['positions'].append((cx, cy))
            
            if current_time - objects[obj_id]['first_seen'] > loiter_threshold:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
                cv2.putText(frame, f"Loitering: {int(current_time - objects[obj_id]['first_seen'])}s", 
                          (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                alert_triggered = True

        if alert_triggered:
            alert.trigger()

        _, jpeg = cv2.imencode('.jpg', frame)
        stframe.image(jpeg.tobytes(), channels="BGR", use_column_width=True)

    cap.release()
    cv2.destroyAllWindows()

# General Detection Function
def start_video_detection(mode):
    alert = AlertSystem()
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    os.makedirs("recordings", exist_ok=True)
    output_path = f"recordings/{mode.replace(' ', '')}_{time.strftime('%Y%m%d_%H%M%S')}.avi"
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
    stframe = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to access camera.")
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        alert_triggered = False

        if mode == "Crowd Management":
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"People Count: {len(faces)}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if len(faces) > 0:
                alert_triggered = True

        elif mode == "Restricted Area Security":
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) > 0:
                alert_triggered = True
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
                cv2.putText(frame, "ALERT! Intruder Detected!", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        elif mode == "Night Time Security":
            cv2.putText(frame, "Monitoring for Night Safety...", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        if alert_triggered:
            alert.trigger()

        out.write(frame)
        _, jpeg = cv2.imencode('.jpg', frame)
        stframe.image(jpeg.tobytes(), channels="BGR", use_column_width=True)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    st.success(f"Recording saved: {output_path}")

# Run selected mode
if selected_section == "Fire & Smoke Detection":
    detect_fire_smoke()
elif selected_section == "Loitering Detection":
    detect_loitering()
elif selected_section:
    start_video_detection(selected_section)