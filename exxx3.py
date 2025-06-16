import cv2
import numpy as np

def detect_fire_smoke(video_path=0):  # Use 0 for webcam or pass video file path
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Resize for faster processing
        frame = cv2.resize(frame, (640, 480))

        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Fire color range in HSV (tuned for orange/yellow flames)
        lower_fire = np.array([18, 50, 50])
        upper_fire = np.array([35, 255, 255])

        # Smoke is usually gray/white, low saturation
        lower_smoke = np.array([0, 0, 100])
        upper_smoke = np.array([180, 50, 255])

        # Create masks
        fire_mask = cv2.inRange(hsv, lower_fire, upper_fire)
        smoke_mask = cv2.inRange(hsv, lower_smoke, upper_smoke)

        # Apply morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel)
        smoke_mask = cv2.morphologyEx(smoke_mask, cv2.MORPH_OPEN, kernel)

        # Find contours for fire and smoke
        contours_fire, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_smoke, _ = cv2.findContours(smoke_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw fire detections
        for cnt in contours_fire:
            area = cv2.contourArea(cnt)
            if area > 500:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(frame, "Fire Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Draw smoke detections
        for cnt in contours_smoke:
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (200, 200, 200), 2)
                cv2.putText(frame, "Smoke Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        cv2.imshow("Fire & Smoke Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Run the detection
detect_fire_smoke()
