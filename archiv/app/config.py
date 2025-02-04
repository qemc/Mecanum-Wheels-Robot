import depthai as dai
import cv2
import numpy as np
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)
try:
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.createColorCamera()
    
    # Set preview size first - must match calibration resolution
    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(30)

    xout = pipeline.createXLinkOut()
    xout.setStreamName("video")
    cam_rgb.preview.link(xout.input)

    device = dai.Device(pipeline)
    calibData = device.readCalibration()
    
    # Get calibration data - keep in pixels
    K_original = np.array(calibData.getCameraIntrinsics(dai.CameraBoardSocket.RGB, 640, 480))
    dist_coeffs = np.array(calibData.getDistortionCoefficients(dai.CameraBoardSocket.RGB))

    # Use original camera matrix without scaling
    camera_matrix = K_original
    
    print(f"Camera Matrix:\n{camera_matrix}")
    print(f"Distortion Coefficients: {dist_coeffs}")

    video_queue = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    print("DepthAI device initialized successfully.")

except Exception as e:
    print(f"Failed to initialize DepthAI device: {e}")
    video_queue = None

# ArUco configuration - marker size in meters
marker_size = 0.08  # 8cm = 0.08m
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
aruco_params = cv2.aruco.DetectorParameters()

# Optimized ArUco detection parameters
aruco_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
aruco_params.cornerRefinementWinSize = 4
aruco_params.cornerRefinementMaxIterations = 50
aruco_params.cornerRefinementMinAccuracy = 0.001
aruco_params.adaptiveThreshWinSizeMin = 5
aruco_params.adaptiveThreshWinSizeMax = 21
aruco_params.adaptiveThreshConstant = 7
aruco_params.minMarkerPerimeterRate = 0.05
aruco_params.maxMarkerPerimeterRate = 4.0
aruco_params.polygonalApproxAccuracyRate = 0.03
aruco_params.minCornerDistanceRate = 0.05