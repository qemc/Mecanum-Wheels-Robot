import cv2
import numpy as np
import math
from config import camera_matrix, aruco_dict, aruco_params, marker_size, dist_coeffs
from shared_data import shared_pose_data
import logging

logger = logging.getLogger(__name__)


import cv2
import numpy as np
import math
from config import camera_matrix, aruco_dict, aruco_params, marker_size, dist_coeffs
import logging

class MarkerDetector:
    def __init__(self, marker_size, camera_matrix, dist_coeffs):
        self.marker_size = marker_size
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.prev_corners = None
        self.smooth_factor = 0.8
        
    def preprocess_image(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        enhanced = cv2.equalizeHist(blurred)
        return enhanced
        
    def refine_corners(self, corners, gray):
        if corners is None:
            return None
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        refined_corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        return refined_corners
        
    def smooth_corners(self, corners):
        if self.prev_corners is None:
            self.prev_corners = corners
            return corners
        smoothed = self.smooth_factor * corners + (1 - self.smooth_factor) * self.prev_corners
        self.prev_corners = smoothed
        return smoothed

    def detect_markers(self, frame):
        # Preprocess image
        processed = self.preprocess_image(frame)
        
        # Detect markers
        corners, ids, rejected = cv2.aruco.detectMarkers(
            processed, 
            aruco_dict,
            parameters=aruco_params,
            cameraMatrix=self.camera_matrix,
            distCoeff=self.dist_coeffs
        )
        
        if ids is None:
            return None, None
            
        # Refine and validate corners
        refined_corners = [self.refine_corners(corner) for corner in corners]
        valid_corners = []
        valid_ids = []
        
        for corner, id in zip(refined_corners, ids):
            if self.validate_marker(corner):
                valid_corners.append(corner)
                valid_ids.append(id)
        
        if not valid_corners:
            return None, None
            
        # Estimate poses with RANSAC
        rvecs, tvecs = self.estimate_pose_ransac(valid_corners)
        return rvecs, tvecs
        
    def validate_marker(self, corners):
        if corners is None:
            return False
        # Check minimum area
        area = cv2.contourArea(corners.reshape(4,2))
        if area < 100:
            return False
        # Check perspective distortion
        rect = cv2.minAreaRect(corners.reshape(4,2))
        aspect_ratio = rect[1][1] / rect[1][0] if rect[1][0] != 0 else 0
        return 0.7 < aspect_ratio < 1.3
        
    def estimate_pose_ransac(self, corners, iterations=100):
        best_error = float('inf')
        best_rvec = None
        best_tvec = None
        
        for _ in range(iterations):
            # Add RANSAC implementation here
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners,
                self.marker_size,
                self.camera_matrix,
                self.dist_coeffs
            )
            # Implement error calculation and best pose selection
            
        return best_rvec, best_tvec

# Initialize detector
detector = MarkerDetector(marker_size, camera_matrix, dist_coeffs)

def detect_aruco_markers(frame):
    rvecs, tvecs = detector.detect_markers(frame)
    # Rest of your existing pose data formatting code
    ...




# Add pose filtering class
class PoseFilter:
    def __init__(self, alpha=0.5):
        self.prev_tvec = None
        self.prev_rvec = None
        self.alpha = alpha

    def filter(self, tvec, rvec):
        if self.prev_tvec is None:
            self.prev_tvec = tvec
            self.prev_rvec = rvec
            return tvec, rvec
        
        # Exponential moving average filter
        filtered_tvec = self.alpha * tvec + (1 - self.alpha) * self.prev_tvec
        filtered_rvec = self.alpha * rvec + (1 - self.alpha) * self.prev_rvec
        
        self.prev_tvec = filtered_tvec
        self.prev_rvec = filtered_rvec
        return filtered_tvec, filtered_rvec

# Initialize pose filters
pallet_filter = PoseFilter()
dropoff_filter = PoseFilter()

def convert_rotation_vector_to_euler_angles(rvec):
    R, _ = cv2.Rodrigues(rvec)
    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return {"x": math.degrees(x), "y": math.degrees(y), "z": math.degrees(z)}

def detect_aruco_markers(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

    pose_data = {
        "timestamp": "",
        "pallet": None,
        "dropoff": None
    }

    if ids is not None and len(ids) > 0:
        try:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, marker_size, camera_matrix, dist_coeffs
            )
            
            for i, id in enumerate(ids.flatten()):
                # Validate marker detection
                marker_area = cv2.contourArea(corners[i].reshape((4,2)))
                if marker_area < 100:
                    continue

                # Apply pose filtering
                filter_to_use = pallet_filter if id == 1 else dropoff_filter
                filtered_tvec, filtered_rvec = filter_to_use.filter(tvecs[i][0], rvecs[i][0])

                # Draw markers
                cv2.aruco.drawDetectedMarkers(frame, corners)
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, filtered_rvec, filtered_tvec, 0.05)

                # Calculate position and orientation
                x = round(filtered_tvec[0], 3)
                y = round(filtered_tvec[1], 3)
                z = round(filtered_tvec[2], 3)

                rotation_deg = convert_rotation_vector_to_euler_angles(filtered_rvec)
                dist = np.linalg.norm(filtered_tvec) * 100  # Convert to cm

                confidence = marker_area / (frame.shape[0] * frame.shape[1])
                
                marker_data = {
                    "orientation": rotation_deg,
                    "position": {"x": x, "y": y, "z": z},
                    "distance": dist,
                    "confidence": confidence
                }

                if id == 1:
                    pose_data["pallet"] = marker_data
                elif id == 2:
                    pose_data["dropoff"] = marker_data

        except cv2.error as e:
            logger.error(f"OpenCV error: {e}")
            pose_data["error"] = "OpenCV pose estimation failed"
        except Exception as e:
            logger.error(f"Error: {e}")
            pose_data["error"] = "Pose estimation failed"

    return pose_data