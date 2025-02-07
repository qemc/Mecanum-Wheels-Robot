# poseEstimator.py

import cv2
import threading
from ArucoDetection.camSetup import DepthAICamera
from ArucoDetection.arucoDetector import ArucoDetector
from .Utils import draw_coordinate_system, draw_tags
from sharedData import shared_data

class PoseEstimator(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
        self.running = False
        self.camera = DepthAICamera()
        self.camera.start()
        
        self.aruco_detector = ArucoDetector(self.camera.camera_matrix)
    
    def run(self):
        self.running = True
        
        while self.running:
            try:
                frame = self.camera.get_frame()
                if frame is None or frame.size == 0:
                    continue
                
                corners, ids = self.aruco_detector.detect_tags(frame)
                
                pose_data = self.aruco_detector.get_pose_data(corners, ids)
                
                if ids is not None and len(pose_data) > 0:
                    draw_tags(frame, corners, ids, pose_data)
                    
                draw_coordinate_system(frame, (frame.shape[1] // 2, frame.shape[0] // 2))
                
                resized_frame = cv2.resize(frame, (640, 360))
                shared_data.set_frame(resized_frame)
                shared_data.set_pose_data(pose_data)
                
                
            except Exception as e:
                print(f"PoseEstimator error: {e}")
                continue
    
    def stop(self):
        self.running = False
        if self.camera:
            self.camera.stop()
