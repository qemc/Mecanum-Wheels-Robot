import depthai as dai
import cv2
import numpy as np

class DepthAICamera:
    def __init__(self, preview_size = (640, 400)):
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


    def get_camera_matrix(self):
        # Return the camera intrinsic matrix
        if self.camera_matrix is None:
            raise RuntimeError("Camera matrix not initialized. Call 'start()' first.")
        return self.camera_matrix
    
    
    def get_dist_coeffs(self):
        # Return the camera intrinsic matrix
        if self.dist_coeffs is None:
            raise RuntimeError("Camera matrix not initialized. Call 'start()' first.")
        return self.dist_coeffs

    def stop(self):
        if self.device:
            self.device.close()

