import cv2
from hand_detector import HandTracker
from drawing import Drawing

def main():
    cap = cv2.VideoCapture(0)
    hand_tracker = HandTracker()
    drawing = Drawing()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        hands, mask_frame = hand_tracker.process(frame_rgb)

        tip = None
        if hands:
            lm = hands[0].landmark
            tip = (int(lm[8].x * frame.shape[1]), int(lm[8].y * frame.shape[0]))
            if hand_tracker.is_index_finger_up(lm):
                drawing.add_point(tip)
            else:
                drawing.add_point(None)

        canvas = drawing.draw()

        # Mostrar as janelas
        cv2.imshow("Hand Detection", mask_frame)
        cv2.imshow("Drawing", canvas)

        if cv2.waitKey(1) & 0xFF == 27:  
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
