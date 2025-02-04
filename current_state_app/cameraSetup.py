import depthai as dai
import cv2
import numpy as np

class DepthAICamera:
    def __init__(self, preview_size=(640, 480), resolution="THE_1080_P", fps=30):
        self.preview_size = preview_size
        self.resolution = resolution
        self.fps = fps
        self.pipeline = None
        self.device = None
        self.video_queue = None
        self.camera_matrix = None

        self._setup_pipeline()

    def _setup_pipeline(self):
        # Initialize pipeline
        self.pipeline = dai.Pipeline()

        # Add camera node
        cam_rgb = self.pipeline.createColorCamera()
        cam_rgb.setPreviewSize(*self.preview_size)
        cam_rgb.setResolution(getattr(dai.ColorCameraProperties.SensorResolution, self.resolution))
        cam_rgb.setInterleaved(False)
        cam_rgb.setFps(self.fps)
        

        # Add XLinkOut for video stream
        xout = self.pipeline.createXLinkOut()
        xout.setStreamName("video")
        cam_rgb.preview.link(xout.input)

    def start(self):
        # Start the pipeline on the device
        self.device = dai.Device(self.pipeline)
        self.video_queue = self.device.getOutputQueue(name="video", maxSize=1, blocking=False)

        # Get camera calibration data
        calib_data = self.device.readCalibration()
        print(np.array(calib_data.getDistortionCoefficients(dai.CameraBoardSocket.RGB)))
        print("dist_co")
        self.camera_matrix = np.array(calib_data.getCameraIntrinsics(dai.CameraBoardSocket.RGB, *self.preview_size))
        
        print(self.camera_matrix)
        print("camera_matrix")
        
    def get_frame(self):
        # Retrieve the latest frame from the video queue
        if self.video_queue is None:
            raise RuntimeError("Camera pipeline not started. Call 'start()' first.")
        frame_data = self.video_queue.get()
        return frame_data.getCvFrame() if frame_data else None

    def get_camera_matrix(self):
        # Return the camera intrinsic matrix
        if self.camera_matrix is None:
            raise RuntimeError("Camera matrix not initialized. Call 'start()' first.")
        return self.camera_matrix

    def stop(self):
        # Release resources
        if self.device is not None:
            self.device.close()
        self.pipeline = None
        self.video_queue = None
        self.camera_matrix = None
