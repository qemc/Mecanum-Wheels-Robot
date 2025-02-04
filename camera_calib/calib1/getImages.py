import cv2
import depthai as dai
import os

def main():
    # Configuration
    chessboard_size = (12, 8)  # (columns, rows) of internal corners
    square_size_cm = 3.0        # Size of a square in cm
    output_dir = 'images/'      # Directory to save calibration images
    image_format = 'png'        # Image format (png, jpg, etc.)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize DepthAI pipeline
    pipeline = dai.Pipeline()

    # Create a color camera node
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setInterleaved(False)
    cam_rgb.setFps(30)

    # Create an output stream
    xout = pipeline.createXLinkOut()
    xout.setStreamName("video")
    cam_rgb.preview.link(xout.input)

    # Connect to the device and start the pipeline
    try:
        device = dai.Device(pipeline)
        video_queue = device.getOutputQueue(name="video", maxSize=1, blocking=False)
        print("DepthAI device initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize DepthAI device: {e}")
        return

    img_count = 0
    print("Press 's' to save an image for calibration, 'Esc' to exit.")

    while True:
        in_video = video_queue.get()
        frame = in_video.getCvFrame()

        cv2.imshow('Calibration Capture - Press "s" to save', frame)
        key = cv2.waitKey(1)

        if key == 27:  # Esc key
            print("Exiting calibration capture.")
            break
        elif key == ord('s'):
            img_path = os.path.join(output_dir, f'calibration_{img_count}.png')
            cv2.imwrite(img_path, frame)
            print(f"Saved {img_path}")
            img_count += 1

    # Cleanup
    device.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
