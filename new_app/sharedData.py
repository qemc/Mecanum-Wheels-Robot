# sharedData.py

class SharedData:
    def __init__(self):
        
        self._frame = None
        self._pose_data = []
        
        
        self._mode = "manul" # 'manual', 'auto' ws:mode
        
        self._start_picking_process = False
        self._picking_status = '-'

        self._forklift_zero = True
        self._forklift_command_up = False
        self._forklift_command_down = False
        self._forklift_status = '-' # 'going up', 'going down', 'steady up', 'steady down'

        
        
        
    
    def set_frame(self, frame):
        self._frame = frame
    
    def get_frame(self):
        return self._frame
    
    def set_pose_data(self, pose_data):
        self._pose_data = pose_data
    
    def get_pose_data(self):
        return self._pose_data
    
    def set_mode(self, mode):
        self._mode = mode
    
    def get_mode(self):
        return self._mode
    
    

    def set_start_picking_process(self, value):
        self._start_picking_process = value
        
    def get_start_picking_process(self):
        return self._start_picking_process
    
    def set_picking_status(self, value):
        self._start_picking_status = value
        
    def get_picking_status(self):
        return self._start_picking_status
    
    
    
    
    def get_forklift_command_up(self):
        return self._forklift_command_up

    def get_forklift_command_down(self):
        return self._forklift_command_down
    
    def set_forklift_command_up(self, command: bool):
        self._forklift_command_up = command

    def set_forklift_command_down(self, command: bool):
        self._forklift_command_down = command
        
    def get_forklift_status(self):
        return self._forklift_status
    
    def set_forklift_status(self, status: str):
        self._forklift_status = status
        
    def get_forklift_zero(self):
        return self._forklift_zero
    
    def set_forklift_zero(self, stat: bool):
        self._forklift_zero = stat
        
        



# Create a singleton instance
shared_data = SharedData()
