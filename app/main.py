import cv2
from hand_detector import HandTracker
from drawing import Drawing

def main():
    cap = cv2.VideoCapture(0)
    hand_tracker = HandTracker()
    drawing = Drawing()

    THRESHOLD_ON = 3
    THRESHOLD_OFF = 3
    on_counter = 0
    off_counter = 0
    draw_state = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        hands, clean_frame, landmark_frame = hand_tracker.process(frame_rgb)

        tip = None
        if hands:
            lm = hands[0].landmark
            tip = (
                int(lm[8].x * frame.shape[1]),
                int(lm[8].y * frame.shape[0])
            )
            if hand_tracker.is_thumb_and_index_close(lm):
                on_counter += 1
                off_counter = 0
            else:
                off_counter += 1
                on_counter = 0
        else:
            off_counter += 1
            on_counter = 0

        if not draw_state and on_counter >= THRESHOLD_ON:
            draw_state = True
        elif draw_state and off_counter >= THRESHOLD_OFF:
            draw_state = False

        if draw_state and tip is not None:
            drawing.add_point(tip)

        canvas = drawing.draw(clean_frame)
        
        # Mostrar as janelas
        cv2.imshow("Hand Detection", landmark_frame)
        cv2.imshow("Drawing", canvas)

        if cv2.waitKey(1) & 0xFF == 27:  
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
