import numpy as np
import math
import cv2

def calculate_2d_position(pose_t, correction_factor=1.0):
    """
    Calculates the 2D position of an object based on its translation vector.
    Args:
        pose_t (array-like): Translation vector from the tag's pose estimation.
        correction_factor (float): Factor to scale the position (default is 1.0).
    Returns:
        tuple: X and Y coordinates in centimeters.
    """
    x = float(pose_t[0]) * 100 * correction_factor  
    y = float(pose_t[2]) * 100 * correction_factor  
    
    # x = 1
    # y = 1
    
    return x, y


def calculate_yaw_angle(pose_R):
    """
    Calculates the yaw angle (rotation around Y axis) from the rotation matrix.
    Args:
        pose_R (array-like): Rotation matrix from the tag's pose estimation.
    Returns:
        float: Yaw angle in degrees, normalized to [-180, 180], or None if calculation fails.
    """
    try:
        R = np.array(pose_R).reshape((3, 3))
        yaw = np.arctan2(R[2,0], R[2,2])
        yaw_deg = np.degrees(yaw)
        return normalize_angle(yaw_deg)
    except:
        return None
    
    #return  1
    
def normalize_angle(angle_deg):
    """
    Normalizes an angle to the range [-180, 180].
    Args:
        angle_deg (float): Angle in degrees.
    Returns:
        float: Normalized angle in degrees.
    """
    return (angle_deg + 180) % 360 - 180


def draw_coordinate_system(frame, center, size=50):
    
    cv2.arrowedLine(frame, center, (center[0] + size, center[1]), (0, 0, 255), 2, tipLength=0.2)
    cv2.putText(frame, "X", (center[0] + size + 5, center[1]), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.arrowedLine(frame, center, (center[0], center[1] - size), (255, 0, 0), 2, tipLength=0.2)
    cv2.putText(frame, "Y", (center[0], center[1] - size - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
