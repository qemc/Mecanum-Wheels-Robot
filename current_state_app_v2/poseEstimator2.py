import cv2
import threading
from cameraSetup2 import DepthAICamera
from ArucoDetector import ArucoDetector
from mathUtils import draw_coordinate_system
from backend2 import shared_data

class PoseEstimator(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = False
        self.camera = DepthAICamera()
        self.camera.start()
        self.tag_detector = ArucoDetector(
            self.camera.get_camera_matrix(),
            self.camera.get_dist_coeffs()
        )

    def format_pose_data(self, detections):
        pose_data = []
        for corner, id, rvec, tvec in detections:
            x_cm, z_cm, yaw = self.tag_detector.calculate_pose(tvec, rvec)
            pose_data.append({
                "id": int(id[0]),
                "x_cm": float(x_cm),
                "y_cm": float(tvec[0][1] * 100),
                "Yaw": float(yaw)
            })
        return pose_data

    def run(self):
        self.running = True
        while self.running:
            frame = self.camera.get_frame()
            if frame is None:
                continue
            
            # Draw coordinate system
            height, width = frame.shape[:2]
            draw_coordinate_system(frame, (width//2, height//2))
            
            # Detect markers and format data for frontend
            detections, frame = self.tag_detector.detect_tags(frame)
            pose_data = self.format_pose_data(detections)
            
            # Update shared data
            shared_data.set_frame(cv2.resize(frame, (640,360)))
            shared_data.set_pose_data(pose_data)
            
    def stop(self):
        self.running = False
        if self.camera:
            self.camera.stop()