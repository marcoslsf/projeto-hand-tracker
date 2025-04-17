import cv2
import mediapipe as mp
from drawing import Drawing

def main():
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5)
    drawing = Drawing()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        mask = frame.copy()

        if result.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(result.multi_hand_landmarks):
                mp_drawing.draw_landmarks(mask, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                lm = hand_landmarks.landmark
                h, w, _ = frame.shape
                index_finger_tip = lm[8]
                thumb_tip = lm[4]
                ix, iy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)

                pinch_distance = ((ix - tx) ** 2 + (iy - ty) ** 2) ** 0.5

                if pinch_distance < 40:
                    drawing.process_point((ix, iy), frame, hand_id=i)
                else:
                    drawing.process_point(None, frame, hand_id=i)

        output = drawing.draw(frame)
        cv2.imshow("Drawing", output)
        cv2.imshow("Mascara", mask)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
