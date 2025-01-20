import numpy as np

class Target:
    
    def __init__(self):
        
        self.x = 0
        self.y = 0
        self.angle = 0
        self.angle_rad = 0
    
    def getPoseData(self, pose, id):
    
        if len(pose) > 0:
            
            for x in pose:
                if x.get("id") == id:
                    
                    self.angle, self.x, self.y = self.getPoseValues(x)
                    self.angle_rad = np.radians(self.angle)
                    
                    return True
                    
                else:
                    self.angle, self.x, self.y = self.getPoseValues(None)
        else:
            self.angle, self.x, self.y = self.getPoseValues(None)
            
            
    def getPoseValues(self, target):
        
        target_x = "Not Visible"
        target_y = "Not Visible"
        target_angle = "Not Visible"    
        
        if target != None :
            
            target_angle = -target.get('Roll')
            target_x = target.get('x_cm')
            target_y = target.get('z_cm')

           
        return target_angle, target_x, target_y
    