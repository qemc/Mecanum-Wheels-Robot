from dataclasses import dataclass
import threading
import time
import CommandHandler

@dataclass
class MotorData:
    
    current_rpm = 0
    target_rpm = 0
    error_pid = 0
    pwm_value = 0
    
    kp = 0
    kd = 0
    ki = 0
    
    
def parse_data(line):
    pass
    
class MotorControlData (threading.Thread):
    
    def __init__(self,commandHandler: CommandHandler):
        self.commandHandler = commandHandler
        self.running = False
        self.update_interval = 0.2
        threading.Thread.__init__(self)
        
    def run(self):
        
        self.running = True
        
        
        while self.running:              
            

            
            data = self.commandHandler.readUART() 
            print(data)
            
            time.sleep(0.1)
