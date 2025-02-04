# app/shared_data.py
import asyncio

class SharedPoseData:
    def __init__(self):
        self._data = {}
        self._lock = asyncio.Lock()

    async def update(self, new_data):
        async with self._lock:
            self._data = new_data

    async def get_data(self):
        async with self._lock:
            return self._data

shared_pose_data = SharedPoseData()
