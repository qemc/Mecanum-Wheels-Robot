from threading import Thread
from poseEstimator2 import PoseEstimator
from exeRobotControl2 import ExeRobotControl
from sharedData import shared_data


def initialize_all():
    """Initialize all subsystems"""
    print("Initializing all subsystems...")
    
    try:
        # Initialize vision system
        pose_estimator = PoseEstimator()
        pose_estimator.start()
        print("Pose estimation initialized")

        # # Initialize robot control system
        # robot_control = ExeRobotControl()
        # robot_control.start()
        # print("Robot control initialized")
        
        # Set initial mode
        shared_data.set_mode(0)
        
        print("All subsystems initialized!")
        
    except Exception as e:
        print(f"Initialization failed: {e}")
        raise
