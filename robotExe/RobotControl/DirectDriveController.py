# from RobotControl.RobotUtils import kinematics
# from RobotControl.Target import Target
# from RobotControl.CommandHandler import CommandHandler

# class DirectDriveController():
    
#     def __init__(self):
        
#         self.fl_prev = 0.0
#         self.fr_prev = 0.0
#         self.rl_prev = 0.0
#         self.rr_prev = 0.0
        
#         self.kp_x = 8.5
        
#     def Proportional(self, current_x, desired_x):
        
#         return (desired_x - current_x) * self.kp_x
        
    
#     def directDrive(self, commandHandler: CommandHandler, target: Target, desired_x):

#         if target.y != "Not Visible":
            
#             angle = target.angle 
#             x= self.Proportional(target.x, desired_x)
#             y= target.y 
            
#             fl, fr, rl, rr = kinematics(x, y, angle)
            
#             fl = round(fl)
#             fr = round(fr)
#             rl = round(rl)
#             rr = round(rr)
            
#             if fl != self.fl_prev:
#                 commandHandler.setFLSpeed(fl)
#                 self.fl_prev = fl
        
#             if fr != self.fr_prev:
#                 commandHandler.setFRSpeed(fr)
#                 self.fr_prev = fr
            
#             if rl != self.rl_prev:
#                 commandHandler.setRLSpeed(rl)
#                 self.rl_prev = rl
                
#             if rr != self.rr_prev:
#                 commandHandler.setRRSpeed(rr)
#                 self.rr_prev = rr    
                
#     def resetWheelsSpeed(self):
        
#         self.fl_prev = 0
#         self.fr_prev = 0
#         self.rl_prev = 0
#         self.rr_prev = 0






from RobotControl.RobotUtils import kinematics
from RobotControl.Target import Target
from RobotControl.CommandHandler import CommandHandler

class DirectDriveController():
    
    def __init__(self):
        self.fl_prev = 0.0
        self.fr_prev = 0.0
        self.rl_prev = 0.0
        self.rr_prev = 0.0
        
 
        self.kp_x = 8.5
        self.kd_x = 1
        self.prev_error_x = 0.0
        self.dt = 1  


    
    def ProportionalDerivative(self, current_value, desired_value, kp, kd, prev_error):

        error = desired_value - current_value

        proportional = kp * error

        derivative = kd * (error - prev_error) / self.dt

        return proportional + derivative, error
    
    def directDrive(self, commandHandler: CommandHandler, target: Target, desired_x):
        if target.y != "Not Visible":
            x, self.prev_error_x = self.ProportionalDerivative(
                target.x, desired_x, self.kp_x, self.kd_x, self.prev_error_x
            )

            angle = target.angle
            y = target.y
            

            fl, fr, rl, rr = kinematics(x, y, angle)
            
            fl = round(fl)
            fr = round(fr)
            rl = round(rl)
            rr = round(rr)
            
            # Wysyłanie prędkości tylko, jeśli uległy zmianie
            if fl != self.fl_prev:
                commandHandler.setFLSpeed(fl)
                self.fl_prev = fl
        
            if fr != self.fr_prev:
                commandHandler.setFRSpeed(fr)
                self.fr_prev = fr
            
            if rl != self.rl_prev:
                commandHandler.setRLSpeed(rl)
                self.rl_prev = rl
                
            if rr != self.rr_prev:
                commandHandler.setRRSpeed(rr)
                self.rr_prev = rr    
                
    def resetWheelsSpeed(self):
        """
        Reset prędkości kół i błędów kontrolerów.
        """
        self.fl_prev = 0
        self.fr_prev = 0
        self.rl_prev = 0
        self.rr_prev = 0
        self.prev_error_x = 0.0
        self.prev_error_angle = 0.0
