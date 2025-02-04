import depthai as dai
import cv2
import numpy as np
from pupil_apriltags import Detector
import os
import math

os.environ["QT_QPA_PLATFORM"] = "xcb"

def calculate_2d_position(pose_t, correction_factor):
    x = float(pose_t[0]) * 100 * correction_factor  # Left/Right in cm
    y = float(pose_t[2]) * 100 * correction_factor  # Forward/Backward in cm
    return x, y

def calculate_yaw_angle(pose_R):
    R = np.array(pose_R).reshape((3, 3))  # Ensure pose_R is reshaped as a 3x3 matrix
    
    # Yaw calculation: atan2 of the Z-axis projection
    yaw = math.atan2(R[2, 0], R[2, 2])  # This ensures proper Z-axis alignment
    yaw_deg = math.degrees(yaw)
    
    # Normalize to -180 to 180
    return (yaw_deg + 180) % 360 - 180

def draw_coordinate_system(frame, center, size=50):
    # X-axis (Red)
    cv2.arrowedLine(frame, center, (center[0] + size, center[1]), (0, 0, 255), 2, tipLength=0.2)
    cv2.putText(frame, "X", (center[0] + size + 5, center[1]), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Y-axis (Blue)
    cv2.arrowedLine(frame, center, (center[0], center[1] - size), (255, 0, 0), 2, tipLength=0.2)
    cv2.putText(frame, "Y", (center[0], center[1] - size - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


def main():
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(30)

    xout = pipeline.createXLinkOut()
    xout.setStreamName("video")
    cam_rgb.preview.link(xout.input)

    device = dai.Device(pipeline)
    calibData = device.readCalibration()
    camera_matrix = np.array(calibData.getCameraIntrinsics(dai.CameraBoardSocket.RGB, 640, 480))

    detector = Detector(
        families='tag36h11',
        nthreads=4,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=1,
        decode_sharpening=0.25,
        debug=0
    )

    video_queue = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    
    TAG_SIZE = 0.10  # 10cm tag
    CORRECTION_FACTOR = 1.1  # Calibrated correction

    try:
        while True:
            frame_data = video_queue.get()
            if frame_data is None:
                continue
                
            frame = frame_data.getCvFrame()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            
            try:
                tags = detector.detect(
                    gray,
                    estimate_tag_pose=True,
                    camera_params=[
                        camera_matrix[0,0],
                        camera_matrix[1,1],
                        camera_matrix[0,2],
                        camera_matrix[1,2]
                    ],
                    tag_size=TAG_SIZE
                )
                
                frame_center = (frame.shape[1]//2, frame.shape[0]//2)
                draw_coordinate_system(frame, frame_center)
                
                for tag in tags:
                    corners = tag.corners.astype(int)
                    center = tuple(tag.center.astype(int))
                    
                    x_cm, y_cm = calculate_2d_position(tag.pose_t, CORRECTION_FACTOR)
                    angle = calculate_yaw_angle(tag.pose_R)
                    
                    cv2.circle(frame, center, 5, (0,255,0), -1)
                    cv2.polylines(frame, [corners.reshape((-1,1,2))], True, (0,255,0), 2)
                    
                    
                    
                    text = f"ID:{tag.tag_id} X:{x_cm:.1f} Y:{y_cm:.1f} R:{angle:.1f}"
                    text_pos = (center[0]-10, center[1]-10)
                    cv2.putText(frame, text, text_pos,
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                    
                    print(f"Tag {tag.tag_id}: X={x_cm:.1f} Y={y_cm:.1f} R={angle:.1f}")
                    
            except Exception as e:
                print(f"Detection error: {str(e)}")
                continue
            
            cv2.imshow("AprilTag Detection", frame)
            if cv2.waitKey(1) == ord('q'):
                break
                
    finally:
        cv2.destroyAllWindows()
        detector = None

if __name__ == "__main__":
    main()