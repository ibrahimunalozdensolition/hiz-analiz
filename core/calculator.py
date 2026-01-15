import numpy as np
from typing import List, Dict, Tuple

class Point:
    def __init__(self, x: int, y: int, frame_number: int):
        self.x = x
        self.y = y
        self.frame_number = frame_number
    
    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, frame={self.frame_number})"

class SpeedCalculator:
    def __init__(self, fps: int, pixel_to_um_ratio: float):
        self.fps = fps
        self.pixel_to_um_ratio = pixel_to_um_ratio
        self.points: List[Point] = []
    
    def set_pixel_ratio(self, pixels: float, micrometers: float):
        if pixels > 0 and micrometers > 0:
            self.pixel_to_um_ratio = micrometers / pixels
    
    def add_point(self, x: int, y: int, frame_number: int):
        point = Point(x, y, frame_number)
        self.points.append(point)
        return len(self.points) - 1
    
    def remove_point(self, index: int):
        if 0 <= index < len(self.points):
            self.points.pop(index)
    
    def clear_points(self):
        self.points.clear()
    
    def get_points(self) -> List[Point]:
        return self.points
    
    def calculate_distance_pixels(self, point1: Point, point2: Point) -> float:
        dx = point2.x - point1.x
        dy = point2.y - point1.y
        return np.sqrt(dx**2 + dy**2)
    
    def calculate_distance_um(self, point1: Point, point2: Point) -> float:
        distance_pixels = self.calculate_distance_pixels(point1, point2)
        return distance_pixels * self.pixel_to_um_ratio
    
    def calculate_time(self, point1: Point, point2: Point) -> float:
        frame_diff = abs(point2.frame_number - point1.frame_number)
        return frame_diff / self.fps if self.fps > 0 else 0
    
    def calculate_speed(self, point1: Point, point2: Point) -> Dict:
        distance_pixels = self.calculate_distance_pixels(point1, point2)
        distance_um = self.calculate_distance_um(point1, point2)
        time_seconds = self.calculate_time(point1, point2)
        
        speed_um_per_sec = distance_um / time_seconds if time_seconds > 0 else 0
        speed_mm_per_sec = speed_um_per_sec / 1000
        
        return {
            'point1': point1,
            'point2': point2,
            'distance_pixels': distance_pixels,
            'distance_um': distance_um,
            'distance_mm': distance_um / 1000,
            'frame_diff': abs(point2.frame_number - point1.frame_number),
            'time_seconds': time_seconds,
            'speed_um_per_sec': speed_um_per_sec,
            'speed_mm_per_sec': speed_mm_per_sec
        }
    
    def calculate_all_consecutive(self) -> List[Dict]:
        if len(self.points) < 2:
            return []
        
        results = []
        for i in range(len(self.points) - 1):
            result = self.calculate_speed(self.points[i], self.points[i + 1])
            result['pair_index'] = f"{i+1}-{i+2}"
            results.append(result)
        
        return results
    
    def get_summary_text(self) -> str:
        if len(self.points) < 2:
            return "En az 2 nokta seçmelisiniz."
        
        results = self.calculate_all_consecutive()
        
        lines = []
        lines.append("=" * 60)
        lines.append("HESAPLAMA SONUÇLARI")
        lines.append("=" * 60)
        lines.append(f"FPS: {self.fps}")
        lines.append(f"Piksel Oranı: {1/self.pixel_to_um_ratio:.2f} pixel = 1000 µm")
        lines.append(f"Toplam Nokta Sayısı: {len(self.points)}")
        lines.append("")
        
        total_distance_pixels = 0
        total_distance_um = 0
        total_distance_mm = 0
        total_time = 0
        total_speed_um = 0
        total_speed_mm = 0
        
        for i, result in enumerate(results, 1):
            lines.append(f"--- Nokta {result['pair_index']} Arası ---")
            lines.append(f"Nokta {i}: Frame {result['point1'].frame_number}, ({result['point1'].x}, {result['point1'].y})")
            lines.append(f"Nokta {i+1}: Frame {result['point2'].frame_number}, ({result['point2'].x}, {result['point2'].y})")
            lines.append(f"Frame Farkı: {result['frame_diff']} frame")
            lines.append(f"Zaman: {result['time_seconds']:.4f} saniye")
            lines.append(f"Mesafe: {result['distance_pixels']:.2f} pixel")
            lines.append(f"Mesafe: {result['distance_um']:.2f} µm ({result['distance_mm']:.4f} mm)")
            lines.append(f"Hız: {result['speed_um_per_sec']:.2f} µm/s ({result['speed_mm_per_sec']:.4f} mm/s)")
            lines.append("")
            
            total_distance_pixels += result['distance_pixels']
            total_distance_um += result['distance_um']
            total_distance_mm += result['distance_mm']
            total_time += result['time_seconds']
            total_speed_um += result['speed_um_per_sec']
            total_speed_mm += result['speed_mm_per_sec']
        
        num_pairs = len(results)
        
        lines.append("=" * 60)
        lines.append("GENEL ORTALAMA")
        lines.append("=" * 60)
        lines.append(f"Nokta Çifti Sayısı: {num_pairs}")
        lines.append("")
        lines.append(f"Ortalama Mesafe: {total_distance_pixels/num_pairs:.2f} pixel")
        lines.append(f"Ortalama Mesafe: {total_distance_um/num_pairs:.2f} µm ({total_distance_mm/num_pairs:.4f} mm)")
        lines.append(f"Ortalama Zaman: {total_time/num_pairs:.4f} saniye")
        lines.append(f"Ortalama Hız: {total_speed_um/num_pairs:.2f} µm/s ({total_speed_mm/num_pairs:.4f} mm/s)")
        lines.append("")
        lines.append(f"Toplam Mesafe: {total_distance_pixels:.2f} pixel")
        lines.append(f"Toplam Mesafe: {total_distance_um:.2f} µm ({total_distance_mm:.4f} mm)")
        lines.append(f"Toplam Zaman: {total_time:.4f} saniye")
        
        return "\n".join(lines)
    
    def export_to_csv(self) -> str:
        if len(self.points) < 2:
            return ""
        
        results = self.calculate_all_consecutive()
        
        lines = []
        lines.append("Nokta Çifti,Frame1,X1,Y1,Frame2,X2,Y2,Frame Farkı,Zaman (s),Mesafe (pixel),Mesafe (µm),Mesafe (mm),Hız (µm/s),Hız (mm/s)")
        
        total_distance_pixels = 0
        total_distance_um = 0
        total_distance_mm = 0
        total_time = 0
        total_speed_um = 0
        total_speed_mm = 0
        
        for result in results:
            line = f"{result['pair_index']},"
            line += f"{result['point1'].frame_number},{result['point1'].x},{result['point1'].y},"
            line += f"{result['point2'].frame_number},{result['point2'].x},{result['point2'].y},"
            line += f"{result['frame_diff']},{result['time_seconds']:.4f},"
            line += f"{result['distance_pixels']:.2f},{result['distance_um']:.2f},{result['distance_mm']:.4f},"
            line += f"{result['speed_um_per_sec']:.2f},{result['speed_mm_per_sec']:.4f}"
            lines.append(line)
            
            total_distance_pixels += result['distance_pixels']
            total_distance_um += result['distance_um']
            total_distance_mm += result['distance_mm']
            total_time += result['time_seconds']
            total_speed_um += result['speed_um_per_sec']
            total_speed_mm += result['speed_mm_per_sec']
        
        num_pairs = len(results)
        
        lines.append("")
        lines.append("ORTALAMA,,,,,,,,,,,,,")
        avg_line = f"Ortalama,,,,,,"
        avg_line += f",{total_time/num_pairs:.4f},"
        avg_line += f"{total_distance_pixels/num_pairs:.2f},{total_distance_um/num_pairs:.2f},{total_distance_mm/num_pairs:.4f},"
        avg_line += f"{total_speed_um/num_pairs:.2f},{total_speed_mm/num_pairs:.4f}"
        lines.append(avg_line)
        
        lines.append("")
        lines.append("TOPLAM,,,,,,,,,,,,,")
        total_line = f"Toplam,,,,,,"
        total_line += f",{total_time:.4f},"
        total_line += f"{total_distance_pixels:.2f},{total_distance_um:.2f},{total_distance_mm:.4f},"
        total_line += f",,"
        lines.append(total_line)
        
        return "\n".join(lines)
