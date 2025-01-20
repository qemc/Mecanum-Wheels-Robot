from ArucoDetection.poseEstimator import PoseEstimator
from sharedData import shared_data
from RobotControl.exeRobotControl import ExeRobotControl

def initialize_all():
    
    estimator = PoseEstimator()
    estimator.start()
    print("PoseEstimator thread started.")

    robot_control = ExeRobotControl()
    robot_control.start()
    print("ExeRobotControl thread started.")

    shared_data.set_mode('manual')