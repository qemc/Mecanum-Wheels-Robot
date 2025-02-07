import cv2
import math
from ArucoDetection.arucoConfig import ArucoConfig
import numpy as np
from .Utils import normalize_angle

class ArucoDetector:
    def __init__(self, camera_matrix):
        
        self.camera_matrix = camera_matrix
        self.tag_config = ArucoConfig()
        self.dictionary = self.tag_config.dictionary
        self.parameters = self.tag_config.parameters
        self.tag_size = self.tag_config.tag_size
        self.correction_factor = self.tag_config.correction_factor
        
        self.detector = cv2.aruco.ArucoDetector(self.dictionary, self.parameters)
    
    def detect_tags(self, frame):
        
        if frame is None:
            return [], None
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)
        
        return corners, ids
    
    def calculate_pose(self, tvec: np.ndarray, rvec: np.ndarray):
        
        x_cm = float(tvec[0][0] * 100)
        z_cm = float(tvec[0][2] * 100 * self.correction_factor)
        rot_mat, _ = cv2.Rodrigues(rvec)
        roll_rad = math.atan2(rot_mat[0, 2], rot_mat[2, 2])
        roll_deg = normalize_angle(math.degrees(roll_rad))
        
        
        return z_cm , x_cm , roll_deg
    
    def get_pose_data(self, corners, ids):
        
        pose_data = []
        if ids is not None:
            
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, self.tag_size, self.camera_matrix, None)

            for i, marker_id in enumerate(ids.flatten()):
                
                z_cm, x_cm, roll_deg = self.calculate_pose(tvecs[i], rvecs[i])
                
                pose_data.append({
                    "id": int(marker_id),            
                    "x_cm": float(x_cm),             
                    "z_cm": float(z_cm),             
                    "Roll": float(roll_deg),         
                })
                
        return pose_data
    
