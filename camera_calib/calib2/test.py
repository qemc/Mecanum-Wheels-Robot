import depthai as dai
import cv2

# Create a pipeline
pipeline = dai.Pipeline()

# Create and configure the RGB camera
cam_rgb = pipeline.createColorCamera()
cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)  # Set to 4K
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
cam_rgb.setFps(30)  # Set desired FPS

# Create an XLink output for the RGB camera
xout_rgb = pipeline.createXLinkOut()
xout_rgb.setStreamName("rgb")
cam_rgb.video.link(xout_rgb.input)

# Connect to the device and start the pipeline
with dai.Device(pipeline) as device:
    print("Starting the camera...")

    # Get the RGB output queue
    rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    while True:
        # Get the latest frame
        rgb_frame = rgb_queue.get()
        frame = rgb_frame.getCvFrame()

        # Display the frame
        cv2.imshow("RGB Camera (4K)", frame)

        # Break on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
s