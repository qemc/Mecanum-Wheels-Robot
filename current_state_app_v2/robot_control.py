from enum import Enum
import math
import numpy as np

class RobotState(Enum):
    SEARCHING_TAG1 = 1
    ALIGNING_TO_TAG1 = 2
    PICKING_PALLET = 3
    SEARCHING_TAG2 = 4
    ALIGNING_TO_TAG2 = 5
    DROPPING_PALLET = 6
    FINISHED = 7

class RobotController:
    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.state = RobotState.SEARCHING_TAG1
        
        # Control parameters
        self.kp_x = 0.8  # Proportional gain for x position
        self.kp_y = 0.6  # Proportional gain for y position
        self.kp_angle = 1.0  # Proportional gain for angle
        
        # Target parameters
        self.target_distance = 30  # cm
        self.x_threshold = 0.5    # cm
        self.angle_threshold = 5  # degrees
        
    def calculate_wheel_velocities(self, vx, vy, omega):
        """Calculate wheel velocities for mecanum drive"""
        # Limit input values to [-100, 100]
        fl = np.clip(vx - vy - omega, -100, 100)
        fr = np.clip(vx + vy + omega, -100, 100)
        rl = np.clip(vx + vy - omega, -100, 100)
        rr = np.clip(vx - vy + omega, -100, 100)
        return fl, fr, rl, rr

    def format_speed_command(self, fl, fr, rl, rr):
        """Format the UART command string"""
        return f"SET_SPEED;fl:{int(fl)};fr:{int(fr)};rl:{int(rl)};rr:{int(rr)};"

    def _is_at_target(self, pose_data, tag_id):
        """Check if robot is aligned with target"""
        target_tag = next((tag for tag in pose_data if tag['id'] == tag_id), None)
        if target_tag:
            return (abs(target_tag['y_cm'] - self.target_distance) < 2 and 
                    abs(target_tag['x_cm']) < self.x_threshold and 
                    abs(target_tag['Yaw']) < self.angle_threshold)
        return False

    def process_pose_data(self, pose_data):
        """Process pose data and generate control commands"""
        if not pose_data:
            return None

        target_id = 1 if self.state in [RobotState.SEARCHING_TAG1, RobotState.ALIGNING_TO_TAG1] else 2
        target_tag = next((tag for tag in pose_data if tag['id'] == target_id), None)

        if target_tag:
            # Calculate errors
            x_error = target_tag['x_cm']  # Target x = 0
            y_error = target_tag['y_cm'] - self.target_distance
            angle_error = target_tag['Yaw']

            # Calculate control inputs
            vx = self.kp_x * x_error
            vy = self.kp_y * y_error
            omega = self.kp_angle * angle_error

            fl, fr, rl, rr = self.calculate_wheel_velocities(vx, vy, omega)
            return self.format_speed_command(fl, fr, rl, rr)

        return "SET_SPEED;fl:0;fr:0;rl:0;rr:0;"  # Stop if no tag found
    
    
    def calculate_wheel_speeds(self, pose_data):
        """Alias for calculate_wheel_velocities with pose data processing"""
        if not pose_data:
            return 0, 0, 0, 0
            
        target_id = 1 if self.state in [RobotState.SEARCHING_TAG1, RobotState.ALIGNING_TO_TAG1] else 2
        target_tag = next((tag for tag in pose_data if tag['id'] == target_id), None)
        
        if target_tag:
            # Calculate errors
            x_error = target_tag['x_cm']
            y_error = target_tag['y_cm'] - self.target_distance
            angle_error = target_tag['Yaw']

            # Calculate control inputs
            vx = self.kp_x * x_error
            vy = self.kp_y * y_error
            omega = self.kp_angle * angle_error

            return self.calculate_wheel_velocities(vx, vy, omega)
            
        return 0, 0, 0, 0