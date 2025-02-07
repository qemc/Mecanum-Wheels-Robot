from gpiozero import LED, Button
import time
from sharedData import shared_data

class ForkliftController:
    
    def __init__(self):

        self.in1 = LED(14)
        self.in2 = LED(15)
        self.in3 = LED(23)
        self.in4 = LED(24)

        self.down_pin = Button(17)

        self.step_sequence = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1]
        ]

        self.step_delay = 0.0007  
        
    def set_pins(self, step):

        self.in1.value = step[0]
        self.in2.value = step[1]
        self.in3.value = step[2]
        self.in4.value = step[3]

    def move_forklift_up(self, duration=25):

        
        shared_data.set_forklift_status('Going up')
        
        start_time = time.time()

        while (time.time() - start_time) < duration:
            for step in self.step_sequence:
                self.set_pins(step)
                time.sleep(self.step_delay)

        self.set_pins([0, 0, 0, 0])  
        
        shared_data.set_forklift_status('Steady up')
        
        shared_data.set_forklift_command_up(False)


    def move_forklift_down(self, zero: bool):

        shared_data.set_forklift_status('Going down')
        
        if zero:
            print("Zero in progress")
        
        while not self.down_pin.is_pressed:
            for step in reversed(self.step_sequence):
                self.set_pins(step)
                time.sleep(self.step_delay)

        self.set_pins([0, 0, 0, 0])  
        
        shared_data.set_forklift_status('Steady down')
        shared_data.set_forklift_command_down(False)
        
        if zero:
            print("Zero done")
            
    def forklift_zero(self):
        
        self.move_forklift_down(True)
        shared_data.set_forklift_zero(False)
        