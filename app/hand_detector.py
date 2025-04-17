import cv2
import mediapipe as mp
import math

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

    def calc_distance(self, p1, p2):
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    def is_thumb_and_index_close(self, landmarks):
        index_tip = (landmarks[8].x, landmarks[8].y)
        thumb_tip = (landmarks[4].x, landmarks[4].y)
        distance = self.calc_distance(index_tip, thumb_tip)
        threshold = 0.05
        return distance < threshold

    def process(self, frame_rgb):
        result = self.hands.process(frame_rgb)
        frame_output = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        clean_frame = frame_output.copy()
        landmark_frame = frame_output.copy()

        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(landmark_frame, hand, self.mp_hands.HAND_CONNECTIONS)
            return result.multi_hand_landmarks, clean_frame, landmark_frame
        return None, clean_frame, landmark_frame


