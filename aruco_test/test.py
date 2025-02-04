import cv2
import numpy as np
import depthai as dai
import math
from typing import Optional, Tuple


class OAKDCamera:
    def __init__(self, preview_size: Tuple[int, int] = (640, 400)):
        self.preview_size = preview_size
        self.pipeline = dai.Pipeline()
        self.device = None
        self.video_queue = None
        self.camera_matrix = None
        self.dist_coeffs = None
        self._setup_pipeline()

    def _setup_pipeline(self):
        cam_rgb = self.pipeline.createColorCamera()
        xout_video = self.pipeline.createXLinkOut()
        xout_video.setStreamName("video")
        cam_rgb.setPreviewSize(*self.preview_size)
        cam_rgb.setInterleaved(False)
        cam_rgb.preview.link(xout_video.input)

    def start(self):
        self.device = dai.Device(self.pipeline)
        self.video_queue = self.device.getOutputQueue("video", maxSize=1, blocking=False)
        calib_data = self.device.readCalibration()
        self.camera_matrix = np.array(
            calib_data.getCameraIntrinsics(dai.CameraBoardSocket.RGB, *self.preview_size)
        )
        self.dist_coeffs = np.array(calib_data.getDistortionCoefficients(dai.CameraBoardSocket.RGB))

    def get_frame(self):
        if self.video_queue is None:
            return None
        frame_data = self.video_queue.get()
        if frame_data is not None:
            return frame_data.getCvFrame()
        return None

    def stop(self):
        if self.device:
            self.device.close()


def process_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def normalize_angle(angle):

    return (angle % 360) - 180


def calculate_pose(tvec, rvec, correction_factor=0.82):
    x_cm = tvec[0][0] * 100
    z_cm = tvec[0][2] * 100 * correction_factor
    rot_mat, _ = cv2.Rodrigues(rvec)
    roll_rad = math.atan2(rot_mat[0, 2], rot_mat[2, 2])
    roll_deg = normalize_angle(math.degrees(roll_rad))
    return z_cm, x_cm, roll_deg


def put_text_with_outline(frame, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.5, color=(0, 255, 0),
                          thickness=2, outline_color=(0, 0, 0), outline_thickness=3):
    cv2.putText(frame, text, position, font, font_scale, outline_color, outline_thickness, lineType=cv2.LINE_AA)
    cv2.putText(frame, text, position, font, font_scale, color, thickness, lineType=cv2.LINE_AA)


def detect_markers(frame, detector, camera_matrix, dist_coeffs, tag_size=0.100, correction_factor=0.82):
    processed = process_image(frame)
    corners, ids, _ = detector.detectMarkers(processed)
    
    if ids is not None:
        
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, tag_size, camera_matrix, dist_coeffs)
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        
        for i, marker_id in enumerate(ids.flatten()):
            z_cm, x_cm, roll_deg = calculate_pose(tvecs[i], rvecs[i], correction_factor)
            text = f"ID:{marker_id} Z:{z_cm:.1f}cm X:{x_cm:.1f}cm Roll:{roll_deg:.1f}"
            put_text_with_outline(frame, text, (10, 30 + i * 30), font_scale=0.6, thickness=2, outline_thickness=3)
    return frame


def main():
    camera = OAKDCamera()
    camera.start()
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    try:
        while True:
            frame = camera.get_frame()
            if frame is None:
                continue
            annotated_frame = detect_markers(frame, detector, camera.camera_matrix, camera.dist_coeffs)
            cv2.imshow('ArUco Detection', annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
