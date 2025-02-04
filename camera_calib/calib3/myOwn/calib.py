#!/usr/bin/env python3
import cv2
import depthai as dai
import numpy as np
import os

# For Charuco detection + calibration
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_1000)

# Adjust these to match your printed board
squaresX = 11          # number of squares along X
squaresY = 8           # number of squares along Y
squareLength = 0.04    # 4 cm per square
markerLength = 0.03    # 3 cm marker inside each square

board = cv2.aruco.CharucoBoard_create(
    squaresX, 
    squaresY, 
    squareLength, 
    markerLength, 
    arucoDict
)

# Will hold the captured images
capturedFrames = []

def create_pipeline():
    """
    Create a pipeline that just streams the OAK-D Lite's RGB camera frames.
    """
    pipeline = dai.Pipeline()

    colorCam = pipeline.createColorCamera()
    colorCam.setBoardSocket(dai.CameraBoardSocket.RGB)
    # 1080_P means 1920x1080
    colorCam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    colorCam.setInterleaved(False)
    colorCam.setFps(30)

    xout = pipeline.createXLinkOut()
    xout.setStreamName("rgb")
    colorCam.video.link(xout.input)

    return pipeline

def main():
    # Create data folder for storing frames
    os.makedirs("rgb_captures", exist_ok=True)

    pipeline = create_pipeline()
    with dai.Device(pipeline) as device:
        print("Press SPACE to capture a frame, and 'q' to finish capturing.")
        q_rgb = device.getOutputQueue("rgb", maxSize=4, blocking=False)

        while True:
            in_rgb = q_rgb.tryGet()
            if in_rgb is None:
                continue
            frame = in_rgb.getCvFrame()

            # Show preview
            cv2.imshow("RGB preview", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                print("Finished capturing frames.")
                break
            elif key == 32:  # Spacebar
                # Save this frame
                capturedFrames.append(frame.copy())
                print(f"Captured frame #{len(capturedFrames)}")

        cv2.destroyAllWindows()

    if len(capturedFrames) < 3:
        print("Not enough frames captured to run calibration. Exiting.")
        return

    # --- Perform single-camera Charuco calibration in OpenCV ---
    allCorners = []
    allIds = []
    imageSize = None

    print("Running single-camera Charuco calibration...")
    for i, img in enumerate(capturedFrames):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect ArUco markers
        corners, ids, _ = cv2.aruco.detectMarkers(gray, arucoDict)
        if ids is None or len(corners) == 0:
            print(f"Warning: No markers found in frame #{i}. Skipping.")
            continue

        # Refine + interpolate charuco corners
        retval, charucoCorners, charucoIds = cv2.aruco.interpolateCornersCharuco(
            corners, ids, gray, board
        )
        if charucoIds is not None and len(charucoIds) > 0:
            allCorners.append(charucoCorners)
            allIds.append(charucoIds)
            if imageSize is None:
                imageSize = gray.shape[::-1]  # (width, height)

    if len(allCorners) < 1:
        print("Not enough valid Charuco detections for calibration.")
        return

    # This function does the actual calibration
    flags = 0  # You can adjust if needed
    (calibError, cameraMatrix, distCoeffs, rvecs, tvecs) = cv2.aruco.calibrateCameraCharuco(
        allCorners, allIds, board, imageSize, None, None, flags=flags
    )

    print("=== Calibration Results ===")
    print(f"RMS Reprojection Error: {calibError}")
    print("Camera Matrix (3x3):")
    print(cameraMatrix)
    print("Distortion Coefficients:")
    print(distCoeffs.ravel())

    # Optionally, save results to a file
    np.savez("camera_calibration.npz",
             rms=calibError,
             camera_matrix=cameraMatrix,
             dist_coeffs=distCoeffs)

if __name__ == "__main__":
    main()

