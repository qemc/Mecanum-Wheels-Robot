class SharedData:
    def __init__(self):
        """Initialize shared data storage"""
        self._frame = None
        self._pose_data = []
        self._mode = 0
        self._pid_stats = {}  # For storing PID performance data if needed

    def set_frame(self, frame):
        """Set current frame"""
        self._frame = frame

    def get_frame(self):
        """Get current frame"""
        return self._frame

    def set_pose_data(self, pose_data):
        """Set current pose data"""
        self._pose_data = pose_data

    def get_pose_data(self):
        """Get current pose data"""
        return self._pose_data

    def set_mode(self, mode):
        """Set current mode"""
        self._mode = mode

    def get_mode(self):
        """Get current mode"""
        return self._mode

    def update_pid_stats(self, stats):
        """Update PID controller statistics"""
        self._pid_stats.update(stats)

    def get_pid_stats(self):
        """Get PID controller statistics"""
        return self._pid_stats

# Create singleton instance
shared_data = SharedData()