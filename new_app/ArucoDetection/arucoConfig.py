import cv2

class ArucoConfig:
    def __init__(self, 
                 dictionary=cv2.aruco.DICT_4X4_50, 
                 parameters=None, 
                 tag_size=0.08, 
                 correction_factor=1.36):
        
        
        self.tag_size = tag_size
        self.correction_factor = correction_factor
        self.dictionary = cv2.aruco.getPredefinedDictionary(dictionary)
        self.parameters = parameters if parameters else cv2.aruco.DetectorParameters()
