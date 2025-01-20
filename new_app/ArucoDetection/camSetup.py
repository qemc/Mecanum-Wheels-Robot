import numpy as np
import depthai as dai

class DepthAICamera:
    def __init__(self, preview_size = (640, 480),
                 resolution = "THE_1080_P", 
                 fps = 30):
        
        self.preview_size = preview_size
        self.resolution = resolution
        self.fps = fps
        self.pipeline = dai.Pipeline()
        self.device = None
        self.video_queue = None
        self.camera_matrix = None
        self._setup_pipeline()

    def _setup_pipeline(self):
        
        cam_rgb = self.pipeline.createColorCamera()
        xout_video = self.pipeline.createXLinkOut()
        xout_video.setStreamName("video")

        cam_rgb.setPreviewSize(*self.preview_size)
        cam_rgb.setResolution(getattr(dai.ColorCameraProperties.SensorResolution, self.resolution))
        cam_rgb.setInterleaved(False)
        cam_rgb.setFps(self.fps)
        cam_rgb.preview.link(xout_video.input)

    def start(self):
        self.device = dai.Device(self.pipeline)
        self.video_queue = self.device.getOutputQueue(name="video", maxSize=1, blocking=False)
        calib_data = self.device.readCalibration()
        
        self.camera_matrix = np.array(
            calib_data.getCameraIntrinsics(dai.CameraBoardSocket.RGB, *self.preview_size)
        )

    def get_frame(self):
        
        if self.video_queue is None:
            return None
        frame_data = self.video_queue.get()
        if frame_data is not None:
            return frame_data.getCvFrame()
        return None

