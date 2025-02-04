import board
import adafruit_icm20x
import math
import time
import numpy as np

class IMUHandler:
    def __init__(self):
        i2c = board.I2C()
        self.mpu = adafruit_icm20x.ICM20948(i2c)
        self.calibrate()
        self.alpha = 0.96  # Complementary filter coefficient
        self.prev_time = time.monotonic()
        self.yaw = 0
        self.mag_offsets = {'x': 0, 'y': 0, 'z': 0}
        self.history = []
        self.history_size = 5

    def calibrate(self):
        print("Calibrating IMU... Keep the sensor still")
        samples = 100
        mag_x, mag_y, mag_z = 0, 0, 0
        
        for _ in range(samples):
            mag = self.mpu.magnetic
            mag_x += mag[0]
            mag_y += mag[1]
            mag_z += mag[2]
            time.sleep(0.01)
            
        self.mag_offsets = {
            'x': mag_x / samples,
            'y': mag_y / samples,
            'z': mag_z / samples
        }
        print("Calibration complete")

    def moving_average(self, new_values):
        self.history.append(new_values)
        if len(self.history) > self.history_size:
            self.history.pop(0)
        return {k: np.mean([h[k] for h in self.history]) for k in new_values.keys()}

    def get_orientation(self):
        try:
            current_time = time.monotonic()
            dt = current_time - self.prev_time
            
            # Get raw sensor data
            accel = self.mpu.acceleration
            gyro = self.mpu.gyro
            mag = [
                self.mpu.magnetic[0] - self.mag_offsets['x'],
                self.mpu.magnetic[1] - self.mag_offsets['y'],
                self.mpu.magnetic[2] - self.mag_offsets['z']
            ]

            # Calculate angles from accelerometer
            roll = math.atan2(accel[1], accel[2])
            pitch = math.atan2(-accel[0], math.sqrt(accel[1]**2 + accel[2]**2))

            # Update yaw using complementary filter
            gyro_yaw = self.yaw + gyro[2] * dt
            mag_yaw = math.atan2(
                mag[1] * math.cos(roll) - mag[2] * math.sin(roll),
                mag[0] * math.cos(pitch) + mag[1] * math.sin(roll) * math.sin(pitch) + mag[2] * math.cos(roll) * math.sin(pitch)
            )
            
            # Complementary filter
            self.yaw = self.alpha * gyro_yaw + (1 - self.alpha) * mag_yaw
            
            # Convert to degrees
            orientation = {
                "roll": math.degrees(roll),
                "pitch": math.degrees(pitch),
                "yaw": math.degrees(self.yaw) % 360,
                "gyro": gyro
            }
            
            # Apply moving average filter
            filtered_orientation = self.moving_average(orientation)
            
            self.prev_time = current_time
            return filtered_orientation
            
        except Exception as e:
            print(f"Error reading IMU: {e}")
            return None

def main():
    imu = IMUHandler()
    
    try:
        while True:
            orientation = imu.get_orientation()
            if orientation:
                print(f"Yaw: {orientation['yaw']:.1f}°  ", end='\r')
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")

if __name__ == "__main__":
    main()