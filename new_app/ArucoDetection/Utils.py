# mathUtils.py

import numpy as np
import cv2

def normalize_angle(angle):
    return (angle % 360) - 180

def draw_coordinate_system(frame, center, size = 50):
    
    cv2.arrowedLine(frame, center, (center[0] + size, center[1]), (0, 0, 255), 2, tipLength=0.2)
    cv2.putText(frame, "X", (center[0] + size + 5, center[1]), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.arrowedLine(frame, center, (center[0], center[1] - size), (255, 0, 0), 2, tipLength=0.2)
    cv2.putText(frame, "Y", (center[0], center[1] - size - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


def put_text_with_outline(frame , text, position, 
                            font=cv2.FONT_HERSHEY_SIMPLEX, font_scale = 0.6, 
                            color=(0, 255, 0), thickness = 2, 
                            outline_color=(0, 0, 0), outline_thickness = 3):
    
    cv2.putText(frame, text, position, font, font_scale, outline_color, outline_thickness, lineType=cv2.LINE_AA)
    cv2.putText(frame, text, position, font, font_scale, color, thickness, lineType=cv2.LINE_AA)


def draw_tags(frame, corners, ids, pose_data):
    
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        
        for i, marker_id in enumerate(ids.flatten()):
            
            z_cm = pose_data[i]["z_cm"]
            x_cm = pose_data[i]["x_cm"]
            roll_deg = pose_data[i]["Roll"]
            text = f"ID:{marker_id} Y:{z_cm:.1f}cm X:{x_cm:.1f}cm Roll:{roll_deg:.1f}"
            position = (10, 30 + i * 30)
            put_text_with_outline(frame, text, position)
            
    return frame
