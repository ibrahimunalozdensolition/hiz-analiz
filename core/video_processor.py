import cv2
import numpy as np
from pathlib import Path

class VideoProcessor:
    def __init__(self):
        self.video_path = None
        self.cap = None
        self.fps = 0
        self.total_frames = 0
        self.width = 0
        self.height = 0
        self.current_frame_number = 0
        self.current_frame = None
        
    def load_video(self, video_path):
        if self.cap:
            self.cap.release()
        
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            raise ValueError("Video dosyası açılamadı!")
        
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        ret, self.current_frame = self.cap.read()
        if ret:
            self.current_frame_number = 0
            return True
        return False
    
    def get_video_info(self):
        return {
            'fps': self.fps,
            'total_frames': self.total_frames,
            'width': self.width,
            'height': self.height,
            'duration': self.total_frames / self.fps if self.fps > 0 else 0
        }
    
    def get_frame(self, frame_number):
        if not self.cap:
            return None
        
        if frame_number < 0 or frame_number >= self.total_frames:
            return None
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        
        if ret:
            self.current_frame = frame
            self.current_frame_number = frame_number
            return frame
        return None
    
    def get_current_frame(self):
        return self.current_frame
    
    def next_frame(self):
        if self.current_frame_number < self.total_frames - 1:
            return self.get_frame(self.current_frame_number + 1)
        return None
    
    def previous_frame(self):
        if self.current_frame_number > 0:
            return self.get_frame(self.current_frame_number - 1)
        return None
    
    def get_stabilized_output_path(self, input_path):
        path = Path(input_path)
        stem = path.stem
        parent = path.parent
        return str(parent / f"{stem}_sabitlenen.avi")
    
    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def __del__(self):
        self.release()
