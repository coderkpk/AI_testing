import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Create a black canvas to draw on
canvas = np.zeros((480, 640, 3), dtype=np.uint8)

# Button positions
reset_btn = (10, 10, 100, 50)  # x, y, w, h
close_btn = (530, 10, 100, 50)

drawing = False
prev_point = None

def is_palm_open(hand_landmarks):
    # Check if all fingers are open (simple heuristic)
    tips_ids = [8, 12, 16, 20]
    open_fingers = 0
    for tip_id in tips_ids:
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            open_fingers += 1
    # Thumb
    if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
        open_fingers += 1
    return open_fingers == 5

def is_index_finger_up(hand_landmarks):
    # Index finger tip above pip joint
    return hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y

def is_point_in_rect(point, rect):
    x, y, w, h = rect
    px, py = point
    return x <= px <= x + w and y <= py <= y + h

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # Draw buttons
    cv2.rectangle(frame, (reset_btn[0], reset_btn[1]), (reset_btn[0]+reset_btn[2], reset_btn[1]+reset_btn[3]), (0,255,0), -1)
    cv2.putText(frame, 'Reset', (reset_btn[0]+10, reset_btn[1]+35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.rectangle(frame, (close_btn[0], close_btn[1]), (close_btn[0]+close_btn[2], close_btn[1]+close_btn[3]), (0,0,255), -1)
    cv2.putText(frame, 'Close', (close_btn[0]+10, close_btn[1]+35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            h, w, _ = frame.shape
            index_finger_tip = hand_landmarks.landmark[8]
            cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

            # Check for palm open (wipe)
            if is_palm_open(hand_landmarks):
                canvas[:] = 0
                prev_point = None
                continue

            # Check for drawing gesture (index finger up)
            if is_index_finger_up(hand_landmarks):
                if is_point_in_rect((cx, cy), reset_btn):
                    canvas[:] = 0
                    prev_point = None
                elif is_point_in_rect((cx, cy), close_btn):
                    cap.release()
                    cv2.destroyAllWindows()
                    exit(0)
                else:
                    if prev_point is not None:
                        cv2.line(canvas, prev_point, (cx, cy), (255, 255, 255), 5)  # Changed to white
                    prev_point = (cx, cy)
            else:
                prev_point = None
    else:
        prev_point = None

    # Overlay the canvas on the frame
    mask = canvas.astype(bool)
    frame[mask] = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)[mask]

    cv2.imshow("Finger Drawing", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()