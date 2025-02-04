import cv2
import math
import numpy as np
from ArucoConfig import ArucoConfig

class ArucoDetector:
    def __init__(self, camera_matrix, dist_coeffs):
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.config = ArucoConfig()
        
    def process_image(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)
        
    def calculate_pose(self, tvec, rvec):
        x_cm = tvec[0][0] * 100
        z_cm = tvec[0][2] * 100 * self.config.correction_factor
        rot_mat, _ = cv2.Rodrigues(rvec)
        yaw = math.degrees(math.atan2(rot_mat[1,0], rot_mat[0,0]))
        return x_cm, z_cm, yaw

    def detect_tags(self, frame):
        if frame is None:
            return [], frame

        processed = self.process_image(frame)
        corners, ids, _ = self.config.detector.detectMarkers(processed)
        
        if ids is None:
            return [], frame

        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            corners, self.config.tag_size, self.camera_matrix, self.dist_coeffs)
            
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        
        for i, marker_id in enumerate(ids.flatten()):
            x_cm, z_cm, yaw = self.calculate_pose(tvecs[i], rvecs[i])
            text = f"ID:{marker_id} Z:{z_cm:.1f}cm X:{x_cm:.1f}cm Yaw:{yaw:.1f}"
            self.put_text_with_outline(frame, text, (10, 30 + i * 30))
            
        return list(zip(corners, ids, rvecs, tvecs)), frame
        
    def put_text_with_outline(self, frame, text, position):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, text, position, font, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, text, position, font, 0.6, (0, 255, 0), 2, cv2.LINE_AA)