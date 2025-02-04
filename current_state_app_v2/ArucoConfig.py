import cv2

class ArucoConfig:
    def __init__(self):
        self.tag_size = 0.100
        self.correction_factor = 0.82
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict)

    def get_detector(self): return self.detector
    def get_tag_size(self): return self.tag_size
    def get_correction_factor(self): return self.correction_factor