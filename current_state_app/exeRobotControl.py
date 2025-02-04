import threading
import time
import serial
from sharedData import shared_data
from robot_control import RobotController, RobotState

class ExeRobotControl(threading.Thread):
    def __init__(self, port="/dev/ttyACM1", baudrate=115200):
        threading.Thread.__init__(self)
        self.running = False
        try:
            self.serial = serial.Serial(port, baudrate)
            self.controller = RobotController(self.serial)
            shared_data.set_robot_controller(self.controller)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            raise

    def send_speed_command(self, fl, fr, rl, rr):
        """Send speed command to robot"""
        command = f"SET_SPEED;fl:{int(fl)};fr:{int(fr)};rl:{int(rl)};rr:{int(rr)};\n"
        self.serial.write(command.encode())
        
    def run(self):
        self.running = True
        while self.running:
            try:
                pose_data = shared_data.get_pose_data()
                if pose_data:
                    # Convert pose to wheel speeds
                    fl, fr, rl, rr = self.controller.calculate_wheel_speeds(pose_data)
                    # Send speed command
                    self.send_speed_command(fl, fr, rl, rr)
                time.sleep(0.05)  # 20Hz control loop
            except Exception as e:
                print(f"Error in robot control loop: {e}")
                time.sleep(1)

    def stop(self):
        self.running = False
        if hasattr(self, 'serial') and self.serial.is_open:
            # Stop the robot before closing
            self.serial.write("SET_SPEED;fl:0;fr:0;rl:0;rr:0;".encode())
            self.serial.close()