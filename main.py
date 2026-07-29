import cv2
import mediapipe as mp
import serial
import time
import math

# ---------------- SERIAL ----------------
PORT = "COM3"   # <-- change (e.g. COM3/COM7). On Mac/Linux: "/dev/ttyUSB0" or "/dev/ttyACM0"
BAUD = 115200
ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(2)

# ---------------- SERVO RANGE (YOUR CALIBRATION) ---------------
MIN_US = 700
MAX_US = 2000

# If any finger moves opposite direction, set True for that finger
# order: thumb, index, middle, ring, pinky
INVERT = [False, False, False, False, False]

# send rate (30 fps is good)
SEND_DELAY = 0.03

# ---------------- MEDIAPIPE ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)


def joint_angle(a, b, c):
    # angle at point b from a-b-c
    ax, ay = a
    bx, by = b
    cx, cy = c
    abx, aby = ax - bx, ay - by
    cbx, cby = cx - bx, cy - by
    dot = abx * cbx + aby * cby
    ab = math.hypot(abx, aby) + 1e-6
    cb = math.hypot(cbx, cby) + 1e-6
    cosv = max(-1.0, min(1.0, dot / (ab * cb)))
    return math.degrees(math.acos(cosv))


def bend_from_angle(angle_deg, straight=175, closed=70):
    # 0 = straight/open, 1 = closed/fist
    bend = (straight - angle_deg) / (straight - closed)
    return max(0.0, min(1.0, bend))


def bend_to_us(bend, invert=False):
    bend = max(0.0, min(1.0, bend))
    if invert:
        bend = 1.0 - bend
    return int(MIN_US + bend * (MAX_US - MIN_US))


cap = cv2.VideoCapture(0)

try:
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        if res.multi_hand_landmarks:
            lm = res.multi_hand_landmarks[0].landmark

            def pt(i):
                return (lm[i].x * w, lm[i].y * h)

            # Finger joint angles:
            # Thumb uses 2-3-4, others use MCP-PIP-DIP like 5-6-7 etc.
            thumb_a = joint_angle(pt(2), pt(3), pt(4))
            index_a = joint_angle(pt(5), pt(6), pt(7))
            middle_a = joint_angle(pt(9), pt(10), pt(11))
            ring_a = joint_angle(pt(13), pt(14), pt(15))
            pinky_a = joint_angle(pt(17), pt(18), pt(19))

            # Convert to bend (tweak straight/closed if needed)
            bends = [
                bend_from_angle(thumb_a, straight=170, closed=85),   # thumb
                bend_from_angle(index_a, straight=175, closed=70),   # index
                bend_from_angle(middle_a, straight=175, closed=70),  # middle
                bend_from_angle(ring_a, straight=175, closed=70),    # ring
                bend_from_angle(pinky_a, straight=175, closed=70),   # pinky
            ]

            # Map to microseconds 700..2000
            us_vals = [bend_to_us(bends[i], INVERT[i]) for i in range(5)]

            # Send: thumb,index,middle,ring,pinky
            msg = f"{us_vals[0]},{us_vals[1]},{us_vals[2]},{us_vals[3]},{us_vals[4]}\n"
            ser.write(msg.encode("utf-8"))

            # Debug overlay
            cv2.putText(frame, msg.strip(), (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Hand -> ESP32 MG995", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

        time.sleep(SEND_DELAY)

finally:
    cap.release()
    cv2.destroyAllWindows()
    ser.close()
