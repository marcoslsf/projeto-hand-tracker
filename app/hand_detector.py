import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process(self, frame_rgb):
        result = self.hands.process(frame_rgb)
        frame_output = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR).copy()

        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame_output, hand, self.mp_hands.HAND_CONNECTIONS)
            return result.multi_hand_landmarks, frame_output
        return None, frame_output

    def is_index_finger_up(self, landmarks):
        return landmarks[8].y < landmarks[6].y
