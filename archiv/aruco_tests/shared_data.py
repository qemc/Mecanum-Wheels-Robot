# shared_data.py
import asyncio

class SharedPoseData:
    def __init__(self):
        self.data = {}
        self.lock = asyncio.Lock()
    
    async def update(self, new_data):
        async with self.lock:
            self.data = new_data
    
    async def get_data(self):
        async with self.lock:
            return self.data

shared_pose_data = SharedPoseData()
