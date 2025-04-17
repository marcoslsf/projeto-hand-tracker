import cv2
import numpy as np

class Drawing:
    def __init__(self):
        self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
        self.points = []
        self.line_color = (0, 255, 0)
        self.line_thickness = 5
        self.eraser_mode = False

    
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
            self.eraser_mode = True
        elif event == cv2.EVENT_RBUTTONUP:
            self.eraser_mode = False

    def add_point(self, point):
        if point:
            self.points.append((point, self.eraser_mode))
        else:
            self.points.append((None, self.eraser_mode))

    def draw(self):
        canvas_copy = self.canvas.copy()
        for i in range(1, len(self.points)):
            pt1, erase1 = self.points[i - 1]
            pt2, erase2 = self.points[i]

            if pt1 is None or pt2 is None:
                continue

            color = (0, 0, 0) if erase2 else self.line_color
            thickness = self.line_thickness + 10 if erase2 else self.line_thickness
            cv2.line(canvas_copy, pt1, pt2, color, thickness)

        self.canvas = canvas_copy
        return canvas_copy
