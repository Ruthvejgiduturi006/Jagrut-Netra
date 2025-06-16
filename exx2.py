import cv2
import time
import math

cap = cv2.VideoCapture(0)
fgbg = cv2.createBackgroundSubtractorMOG2()

loiter_threshold = 10  # seconds to consider someone is loitering
min_contour_area = 500

loitering_tracker = {}

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    mask = fgbg.apply(frame)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_time = time.time()

    for cnt in contours:
        if cv2.contourArea(cnt) < min_contour_area:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w // 2, y + h // 2
        object_id = None

        # Try to match to existing object by proximity
        for oid, data in loitering_tracker.items():
            prev_pos = data['position']
            if distance((cx, cy), prev_pos) < 50:
                object_id = oid
                break

        if object_id is None:
            object_id = str(current_time)
            loitering_tracker[object_id] = {
                'position': (cx, cy),
                'first_seen': current_time,
                'last_seen': current_time
            }
        else:
            loitering_tracker[object_id]['last_seen'] = current_time
            loitering_tracker[object_id]['position'] = (cx, cy)

        duration = loitering_tracker[object_id]['last_seen'] - loitering_tracker[object_id]['first_seen']
        if duration > loiter_threshold:
            cv2.putText(frame, f"Loitering! {int(duration)}s", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        else:
            cv2.putText(frame, f"{int(duration)}s", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 1)

    # Cleanup: remove old IDs
    keys_to_remove = [oid for oid in loitering_tracker if current_time - loitering_tracker[oid]['last_seen'] > 3]
    for k in keys_to_remove:
        del loitering_tracker[k]

    cv2.imshow("Loitering Detection", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
