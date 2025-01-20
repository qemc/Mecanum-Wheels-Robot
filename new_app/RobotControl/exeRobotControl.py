import threading
import time
from sharedData import shared_data  
from RobotControl.CommandHandler import CommandHandler
from RobotControl.Target import Target
from RobotControl.DirectDriveController import DirectDriveController
from RobotControl.ForkLiftController import ForkliftController
from RobotControl.RobotUtils import stopRobot, AlignAngle, AlignX, X_THRESHOLD, Y_THRESHOLD, DESIRED_X, AlignBackward, rotate


def put_off_pallet(id, target: Target, commandHandler: CommandHandler, x_align, angle_align, directController: DirectDriveController ):
    
    
    rotate(commandHandler)
    while True:
        pose_data = shared_data.get_pose_data()
        if target.getPoseData(pose_data, id):
            break
    stopRobot(commandHandler)
    time.sleep(1)

    picking_sequence(id, target, commandHandler, x_align, angle_align, directController)
        
    
        



def picking_sequence(id, target: Target, commandHandler: CommandHandler, x_align, angle_align, directController: DirectDriveController):
    
    pose_data = shared_data.get_pose_data()
    target.getPoseData(pose_data, id)
    
    
    if x_align == False and angle_align == False and shared_data.get_start_picking_process() == True  and target.x != "Not Visible":
        
        
        shared_data.set_picking_status("angle aligning")
        if AlignAngle(target.angle, commandHandler):
            
            angle_align = False
            x_align = True
            
            shared_data.set_picking_status("X axe aligning")

            AlignX(target.y, commandHandler, target.angle_rad)
            
            while x_align:
                
                pose_data = shared_data.get_pose_data()
                target.getPoseData(pose_data, id=id)
                
                if target.x != "Not Visible":
                    
                    if target.x < X_THRESHOLD and target.x > -X_THRESHOLD:
                        x_align = False
            
            
            while True:
                
                if target.x != "Not Visible" and target.y < Y_THRESHOLD:
                    break
                
                pose_data = shared_data.get_pose_data()
                target.getPoseData(pose_data, id=id)
                
                shared_data.set_picking_status("Direct driving")

                directController.directDrive(commandHandler, target, DESIRED_X)
                
            stopRobot(commandHandler)
            
            

            return True



            
        
class ExeRobotControl(threading.Thread):
    
    def __init__(self):

        self.running = False
        
        
        self.angle_align_pick = False
        self.x_align_pick = False
        
        self.angle_align_drop = False
        self.x_align_drop = False
        
        
        self.commandHandler = CommandHandler()
        self.target = Target()
        self.directController = DirectDriveController()
        self.forklift = ForkliftController()

        
        threading.Thread.__init__(self)
    
        self.test_previous_picking_status = False
        self.test_previous_forklift_status = False
        
    
    def run(self):
        
            self.running = True
            stopRobot(self.commandHandler)

            while self.running:

                if shared_data.get_forklift_status() == '-':
                    self.forklift.forklift_zero()
                    shared_data.set_forklift_zero(False)
                
                
                if shared_data.get_mode() == 'auto':
                    
                    if shared_data.get_forklift_zero():
                        self.forklift.forklift_zero()
                
                    if shared_data.get_start_picking_process():
                        if picking_sequence(0, self.target, self.commandHandler, 
                                            self.x_align_pick, self.angle_align_pick, 
                                            self.directController):
                    

                            
                            
                            AlignBackward(self.commandHandler)
                            
                            put_off_pallet(1, self.target, self.commandHandler, 
                                            self.x_align_pick, self.angle_align_pick, 
                                            self.directController)
                            
                            shared_data.set_start_picking_process(False)
                            shared_data.set_picking_status("-")
                            
                            
                            
                            
                                
                elif shared_data.get_mode() == 'manual':
                    
                    shared_data.set_picking_status('-')
                    
                    if shared_data.get_forklift_zero():
                        self.forklift.forklift_zero()
                                        


                    if shared_data.get_forklift_status() == 'Steady up' and shared_data.get_forklift_command_down():
                        self.forklift.move_forklift_down(False)
                        
                        
                    if shared_data.get_forklift_status() == 'Steady down' and shared_data.get_forklift_command_up():
                        self.forklift.move_forklift_up()
                        

                

        
