import cv2
import threading
from cameraSetup import DepthAICamera
from aprilTragDetector import AprilTagDetector
from mathUtils import draw_coordinate_system
from backend import shared_data



class PoseEstimator(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = False
        self.camera = DepthAICamera()
        self.camera.start()
        self.tag_detector = AprilTagDetector(self.camera.get_camera_matrix())

    def run(self):
        
        self.running = True
        
        while self.running:
            try:
                
                frame = self.camera.get_frame()
                if frame is None or frame.size == 0: continue
                
                tags = self.tag_detector.detect_tags(frame)
                pose_data = self.tag_detector.get_pose_data(tags)
                
                if pose_data:
                    
                    self.tag_detector.draw_tags(frame, tags)
                
                #print(pose_data)
                
                draw_coordinate_system(frame, (frame.shape[1]//2, frame.shape[0]//2))
                    
                shared_data.set_frame(cv2.resize(frame, (640,360)))
                shared_data.set_pose_data(pose_data)
                    
            except: continue

    def stop(self):
        self.running = False
        if self.camera: self.camera.stop()