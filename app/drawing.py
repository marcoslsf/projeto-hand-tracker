import cv2
import numpy as np

class Drawing:
    def __init__(self):
        self.canvas = None
        self.last_points = [None, None]
        self.line_color = (0, 255, 0)
        self.line_thickness = 5
        self.eraser_modes = [False, False]

        cv2.namedWindow("Drawing")
        cv2.createTrackbar("Espessura", "Drawing", 5, 20, self.update_thickness)
        cv2.createTrackbar("Cor", "Drawing", 0, 2, self.update_color)
        cv2.setMouseCallback("Drawing", self.mouse_callback)

    def update_thickness(self, val):
        self.line_thickness = val if val > 0 else 1

    def update_color(self, val):
        if val == 0:
            self.line_color = (0, 255, 0)
        elif val == 1:
            self.line_color = (0, 0, 255)
        elif val == 2:
            self.line_color = (255, 0, 0)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_RBUTTONDOWN:
            self.eraser_modes = [True, True]
        elif event == cv2.EVENT_RBUTTONUP:
            self.eraser_modes = [False, False]

    def process_point(self, point, frame, hand_id=0):
        if self.canvas is None:
            self.canvas = np.zeros_like(frame)

        if point is None:
            self.last_points[hand_id] = None
            return

        if self.last_points[hand_id] is not None:
            x1, y1 = self.last_points[hand_id]
            x2, y2 = point
            steps = max(abs(x2 - x1), abs(y2 - y1)) // 2
            if steps == 0:  # Adicionada a verificação para evitar divisão por zero
                steps = 1
            for i in range(steps + 1):
                alpha = i / steps
                ix = int(x1 * (1 - alpha) + x2 * alpha)
                iy = int(y1 * (1 - alpha) + y2 * alpha)
                if self.eraser_modes[hand_id]:
                    cv2.circle(self.canvas, (ix, iy), 60, (0, 0, 0), -1)
                else:
                    cv2.circle(self.canvas, (ix, iy), self.line_thickness // 2, self.line_color, -1)

        self.last_points[hand_id] = point

    def draw(self, frame):
        if self.canvas is None:
            return frame
        return cv2.add(frame, self.canvas)
