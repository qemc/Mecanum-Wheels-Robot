import numpy as np
from .CommandHandler import CommandHandler
import time
import math


MIN_RPM = 20
WHEEL_RADIUS = 0.04
PI = np.pi
LXLY = 0.1748
WHEEL_V_MIN = (MIN_RPM * 2 * PI * WHEEL_RADIUS) / 60
DESIRED_ANGLE = 0
ANGLE_THRESHOLD = 2
Y_THRESHOLD = 35
X_THRESHOLD = 2
DESIRED_Y = 35
DESIRED_X = 0
TIMEOUT = 5.0


def linearToRPM(v):
    """Calculates linear speed of each wheel to RPM."""
    return (v * 60) / (2 * PI * WHEEL_RADIUS)


def CalculateRotationTime(angle):
    """Calculates time needed to rotate with min speed to align with the tag angle."""
    print('kat przekazany do obliczen czasu: ', angle)

    omega_z = (MIN_RPM * WHEEL_RADIUS * 2 * PI) / (60 * LXLY)
    angle_rad = math.radians(abs(angle))

    return (angle_rad / omega_z) + 1.5, omega_z


def AlignAngle(angle, commandHandler: CommandHandler):
    """Rotates the robot to align with tag angle."""
    rotationTime, omegaZ = CalculateRotationTime(angle)

    if angle < 0:
        omegaZ = -omegaZ

    fl, fr, rl, rr = kinematics(0, 0, omegaZ)
    commandHandler.sendSpeedCommand(fl, fr, rl, rr)

    startTime = time.time()

    while True:
        elapsed_time = time.time() - startTime
        if elapsed_time >= rotationTime:
            print(f"Rotating for {rotationTime} completed")
            break

    commandHandler.sendSpeedCommand(0, 0, 0, 0)

    return True


def rotate(command_handler: CommandHandler):
    omega_z = -1

    fl, fr, rl, rr = kinematics(0, 0, omega_z)

    command_handler.sendSpeedCommand(fl, fr, rl, rr)


def AlignBackward(comandHandler: CommandHandler):
    """Moves robot backward for 5 seconds to create buffer for alignment."""
    startTime = time.time()

    fl, fr, rl, rr = kinematics(0, -1, 0)

    comandHandler.sendSpeedCommand(fl, fr, rl, rr)

    while True:
        elapsed_time = time.time() - startTime
        if elapsed_time >= 5:
            print(f"Backward for {5} s completed")
            break

    comandHandler.sendSpeedCommand(0, 0, 0, 0)

    return True


def AlignX(v, commandHandler: CommandHandler, angle_rad):
    """Aligns robot in X axis and calls AlignBackward to keep buffer."""
    v_x = v * -np.sin(angle_rad)
    v_y = v * np.cos(angle_rad)

    print("V_x: ", v_x)
    print("V_y:", v_y)

    if v_y < 30:
        if AlignBackward(commandHandler):
            print("Robot has moved backward")

    fl, fr, rl, rr = kinematics(v_x, 0, 0)

    commandHandler.sendSpeedCommand(fl, fr, rl, rr)


def kinematics(vx, vy, omega_z):
    """
    Calculates the speed and direction of each wheel.
    Used for direction assignment and real-time robot alignment with the pallet.
    """
    fl = 1 / WHEEL_RADIUS * (vy - vx - omega_z)
    fr = 1 / WHEEL_RADIUS * (vy + vx + omega_z)
    rl = 1 / WHEEL_RADIUS * (vy + vx - omega_z)
    rr = 1 / WHEEL_RADIUS * (vy - vx + omega_z)

    ratio = WHEEL_V_MIN / min(abs(fl), abs(fr), abs(rl), abs(rr))

    fl *= ratio
    fr *= ratio
    rl *= ratio
    rr *= ratio
    return linearToRPM(fl), linearToRPM(fr), linearToRPM(rl), linearToRPM(rr)


def stopRobot(commandHandler: CommandHandler):
    """Stops the robot."""
    commandHandler.sendSpeedCommand(0, 0, 0, 0)
