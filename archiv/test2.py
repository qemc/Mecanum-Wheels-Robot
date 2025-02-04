import depthai as dai
import cv2
import numpy as np
from pupil_apriltags import Detector
import os

# Force Qt to use xcb (if necessary)
os.environ["QT_QPA_PLATFORM"] = "xcb"

def format_position(pos_array):
    """Safely format position array to string"""
    try:
        return f"X:{float(pos_array[0]):.1f} Y:{float(pos_array[1]):.1f} Z:{float(pos_array[2]):.1f}"
    except:
        return "Invalid position"

def main():
    # Initialize pipeline
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(1280, 720)  # Higher resolution for better detection
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(30)

    xout = pipeline.createXLinkOut()
    xout.setStreamName("video")
    cam_rgb.preview.link(xout.input)

    # Initialize device
    device = dai.Device(pipeline)
    calibData = device.readCalibration()
    camera_matrix = np.array(calibData.getCameraIntrinsics(dai.CameraBoardSocket.RGB, 1280, 720))

    # Initialize detector with optimized parameters for accuracy
    detector = Detector(
        families='tag36h11',
        nthreads=4,  # Utilize multiple threads for faster processing
        quad_decimate=1.0,  # Maintain full resolution
        quad_sigma=0.0,  # No pre-blur
        refine_edges=1,  # Enable edge refinement
        decode_sharpening=0.25,  # Moderate sharpening
        debug=0
    )

    video_queue = device.getOutputQueue(name="video", maxSize=1, blocking=False)

    try:
        while True:
            frame_data = video_queue.get()
            if frame_data is None:
                continue
                
            frame = frame_data.getCvFrame()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization to improve contrast
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
                    tag_size=0.08  # Ensure this matches your physical tag size
                )
                
                for tag in tags:
                    corners = tag.corners.astype(int)
                    center = tuple(tag.center.astype(int))
                    
                    # Draw detection
                    cv2.circle(frame, center, 5, (0, 255, 0), -1)
                    cv2.polylines(frame, [corners.reshape((-1,1,2))], True, (0,255,0), 2)
                    
                    # Format position safely
                    pos_str = format_position(tag.pose_t * 100)  # Convert to centimeters
                    text = f"ID:{tag.tag_id} {pos_str}cm"
                    
                    cv2.putText(frame, text, (center[0]-10, center[1]-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                    
                    print(f"Tag {tag.tag_id} at position: {pos_str}cm")
                    
            except Exception as e:
                print(f"Detection error: {e}")
                continue
            
            cv2.imshow("AprilTag Detection", frame)
            if cv2.waitKey(1) == ord('q'):
                break
                
    finally:
        cv2.destroyAllWindows()
        detector = None  # Explicitly cleanup detector

if __name__ == "__main__":
    main()
