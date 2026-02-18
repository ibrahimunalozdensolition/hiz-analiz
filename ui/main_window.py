from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSlider, QFileDialog, QGroupBox,
                             QStatusBar, QMessageBox, QTextEdit,
                             QListWidget, QListWidgetItem, QSizePolicy, QScrollArea)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QScreen
import cv2
import numpy as np
from pathlib import Path

from core.video_processor import VideoProcessor
from core.calculator import SpeedCalculator
from ui.styles import AppStyles

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_processor = VideoProcessor()
        self.calculator = None
        self.selecting_point = False
        self.video_loaded = False
        self.display_scale = 1.0
        self.video_display_width = 0
        self.video_display_height = 0
        self.zoom_level = 1.0
        self.zoom_offset_x = 0
        self.zoom_offset_y = 0
        self.panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.contrast = 1.0
        self.point_size = 8
        
        self.setWindowTitle("Erytroscope")
        
        screen = self.screen()
        screen_geometry = screen.availableGeometry()
        min_width = int(screen_geometry.width() * 0.7)
        min_height = int(screen_geometry.height() * 0.6)
        self.setMinimumSize(min_width, min_height)
        
        self.init_ui()
        self.setStyleSheet(AppStyles.get_stylesheet())
        
        self.showMaximized()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        left_layout = QVBoxLayout()
        
        title_label = QLabel("Video Display")
        title_label.setObjectName("title")
        left_layout.addWidget(title_label)
        
        self.video_label = QLabel()
        self.video_label.setObjectName("videoLabel")
        
        screen = self.screen()
        screen_geometry = screen.availableGeometry()
        video_min_width = int(screen_geometry.width() * 0.4)
        video_min_height = int(screen_geometry.height() * 0.4)
        self.video_label.setMinimumSize(video_min_width, video_min_height)
        
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setText("Click 'Load Video' button to load a video")
        self.video_label.setStyleSheet(f"""
            QLabel {{
                background-color: {AppStyles.TEXT_BLACK};
                color: white;
                font-size: 16px;
            }}
        """)
        self.video_label.mousePressEvent = self.video_label_mouse_press
        self.video_label.mouseMoveEvent = self.video_label_mouse_move
        self.video_label.mouseReleaseEvent = self.video_label_mouse_release
        self.video_label.setScaledContents(False)
        self.video_display_width = video_min_width
        self.video_display_height = video_min_height
        left_layout.addWidget(self.video_label)
        
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Frame:"))
        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.setEnabled(False)
        self.frame_slider.valueChanged.connect(self.slider_changed)
        slider_layout.addWidget(self.frame_slider)
        self.frame_label = QLabel("0 / 0")
        slider_layout.addWidget(self.frame_label)
        left_layout.addLayout(slider_layout)
        
        zoom_layout = QHBoxLayout()
        self.zoom_in_btn = QPushButton("Zoom In")
        self.zoom_in_btn.setEnabled(False)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("Zoom Out")
        self.zoom_out_btn.setEnabled(False)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)
        
        self.zoom_reset_btn = QPushButton("Reset")
        self.zoom_reset_btn.setEnabled(False)
        self.zoom_reset_btn.clicked.connect(self.zoom_reset)
        zoom_layout.addWidget(self.zoom_reset_btn)
        
        self.zoom_label = QLabel("Zoom: %100")
        self.zoom_label.setContentsMargins(30, 0, 0, 0)
        zoom_layout.addWidget(self.zoom_label)
        left_layout.addLayout(zoom_layout)
        
        main_layout.addLayout(left_layout, 75)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        video_group = QGroupBox("Video Operations")
        video_group.setMinimumHeight(160)
        video_group.setMaximumHeight(200)
        video_group_layout = QVBoxLayout()
        video_group_layout.setSpacing(10)
        
        self.load_video_btn = QPushButton("Load Video")
        self.load_video_btn.clicked.connect(self.load_video)
        video_group_layout.addWidget(self.load_video_btn)
        
        self.video_info_label = QLabel("No video information")
        self.video_info_label.setWordWrap(True)
        self.video_info_label.setMinimumHeight(80)
        self.video_info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        video_group_layout.addWidget(self.video_info_label)
        
        video_group.setLayout(video_group_layout)
        right_layout.addWidget(video_group)
        
        contrast_group = QGroupBox("Contrast Control")
        contrast_group.setMinimumHeight(80)
        contrast_group.setMaximumHeight(120)
        contrast_group_layout = QVBoxLayout()
        contrast_group_layout.setSpacing(10)
        
        contrast_label_layout = QHBoxLayout()
        contrast_label_layout.addWidget(QLabel("Contrast:"))
        self.contrast_value_label = QLabel("1.0")
        self.contrast_value_label.setMinimumWidth(40)
        self.contrast_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        contrast_label_layout.addWidget(self.contrast_value_label)
        contrast_label_layout.addStretch()
        contrast_group_layout.addLayout(contrast_label_layout)
        
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(300)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.contrast_slider.setTickInterval(50)
        self.contrast_slider.valueChanged.connect(self.contrast_changed)
        contrast_group_layout.addWidget(self.contrast_slider)
        
        contrast_group.setLayout(contrast_group_layout)
        right_layout.addWidget(contrast_group)
        
        point_size_group = QGroupBox("Point Size")
        point_size_group.setMinimumHeight(80)
        point_size_group.setMaximumHeight(120)
        point_size_group_layout = QVBoxLayout()
        point_size_group_layout.setSpacing(10)
        
        point_size_label_layout = QHBoxLayout()
        point_size_label_layout.addWidget(QLabel("Size:"))
        self.point_size_value_label = QLabel("8")
        self.point_size_value_label.setMinimumWidth(40)
        self.point_size_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        point_size_label_layout.addWidget(self.point_size_value_label)
        point_size_label_layout.addStretch()
        point_size_group_layout.addLayout(point_size_label_layout)
        
        self.point_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.point_size_slider.setMinimum(3)
        self.point_size_slider.setMaximum(20)
        self.point_size_slider.setValue(8)
        self.point_size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.point_size_slider.setTickInterval(2)
        self.point_size_slider.valueChanged.connect(self.point_size_changed)
        point_size_group_layout.addWidget(self.point_size_slider)
        
        point_size_group.setLayout(point_size_group_layout)
        right_layout.addWidget(point_size_group)
        
        self.pixel_value = 546
        self.um_value = 1000
        
        points_group = QGroupBox("Point Selection")
        points_layout = QVBoxLayout()
        points_layout.setSpacing(10)
        
        self.select_point_btn = QPushButton("Select Point")
        self.select_point_btn.setEnabled(False)
        self.select_point_btn.clicked.connect(self.start_point_selection)
        points_layout.addWidget(self.select_point_btn)
        
        self.points_list = QListWidget()
        self.points_list.setMinimumHeight(120)
        self.points_list.setMaximumHeight(200)
        points_layout.addWidget(self.points_list)
        
        points_buttons_layout = QHBoxLayout()
        self.clear_last_btn = QPushButton("Remove Last")
        self.clear_last_btn.setEnabled(False)
        self.clear_last_btn.clicked.connect(self.clear_last_point)
        points_buttons_layout.addWidget(self.clear_last_btn)
        
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.setEnabled(False)
        self.clear_all_btn.clicked.connect(self.clear_all_points)
        points_buttons_layout.addWidget(self.clear_all_btn)
        points_layout.addLayout(points_buttons_layout)
        
        points_group.setLayout(points_layout)
        right_layout.addWidget(points_group)
        
        calc_group = QGroupBox("Calculation")
        calc_layout = QVBoxLayout()
        calc_layout.setSpacing(10)
        
        self.calculate_btn = QPushButton("Calculate")
        self.calculate_btn.setEnabled(False)
        self.calculate_btn.clicked.connect(self.calculate_speeds)
        calc_layout.addWidget(self.calculate_btn)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(200)
        self.results_text.setPlaceholderText("Results will appear here...")
        calc_layout.addWidget(self.results_text)
        
        self.export_btn = QPushButton("Save Results as CSV")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_results)
        calc_layout.addWidget(self.export_btn)
        
        calc_group.setLayout(calc_layout)
        right_layout.addWidget(calc_group)
        
        right_layout.addStretch()
        
        self.about_btn = QPushButton("About")
        self.about_btn.clicked.connect(self.show_about)
        right_layout.addWidget(self.about_btn)
        
        scroll_area.setWidget(right_widget)
        main_layout.addWidget(scroll_area, 25)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Video", 
            "", 
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_path:
            try:
                if self.video_processor.load_video(file_path):
                    self.video_loaded = True
                    info = self.video_processor.get_video_info()
                    
                    pixels = self.pixel_value
                    um = self.um_value
                    self.calculator = SpeedCalculator(info['fps'], um / pixels)
                    
                    self.video_info_label.setText(
                        f"FPS: {info['fps']}\n"
                        f"Total Frames: {info['total_frames']}\n"
                        f"Resolution: {info['width']}x{info['height']}\n"
                        f"Duration: {info['duration']:.2f} sec"
                    )
                    
                    self.frame_slider.setMaximum(info['total_frames'] - 1)
                    self.frame_slider.setValue(0)
                    self.frame_slider.setEnabled(True)
                    self.select_point_btn.setEnabled(True)
                    self.zoom_in_btn.setEnabled(True)
                    self.zoom_out_btn.setEnabled(True)
                    self.zoom_reset_btn.setEnabled(True)
                    
                    self.selecting_point = False
                    self.select_point_btn.setText("Select Point")
                    self.select_point_btn.setStyleSheet("")
                    
                    self.clear_all_points()
                    self.zoom_reset()
                    
                    self.video_display_width = self.video_label.width()
                    self.video_display_height = self.video_label.height()
                    
                    self.display_frame()
                    self.status_bar.showMessage(f"Video loaded: {Path(file_path).name}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to load video!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Video loading error: {str(e)}")
    
    def slider_changed(self, value):
        if self.video_loaded:
            self.video_processor.get_frame(value)
            self.display_frame()
            self.frame_label.setText(f"{value} / {self.video_processor.total_frames - 1}")
    
    def contrast_changed(self, value):
        self.contrast = value / 100.0
        self.contrast_value_label.setText(f"{self.contrast:.1f}")
        if self.video_loaded:
            self.display_frame()
    
    def point_size_changed(self, value):
        self.point_size = value
        self.point_size_value_label.setText(f"{self.point_size}")
        if self.video_loaded:
            self.display_frame()
    
    def display_frame(self):
        frame = self.video_processor.get_current_frame()
        if frame is not None:
            display_frame = frame.copy()
            
            if self.contrast != 1.0:
                display_frame = cv2.convertScaleAbs(display_frame, alpha=self.contrast, beta=0)
            
            display_frame = self.draw_points_on_frame(display_frame)
            
            if self.zoom_level > 1.0:
                h, w = display_frame.shape[:2]
                crop_w = int(w / self.zoom_level)
                crop_h = int(h / self.zoom_level)
                
                center_x = w // 2 + self.zoom_offset_x
                center_y = h // 2 + self.zoom_offset_y
                
                x1 = max(0, center_x - crop_w // 2)
                y1 = max(0, center_y - crop_h // 2)
                x2 = min(w, x1 + crop_w)
                y2 = min(h, y1 + crop_h)
                
                x1 = max(0, x2 - crop_w)
                y1 = max(0, y2 - crop_h)
                
                display_frame = display_frame[y1:y2, x1:x2]
            
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            pixmap = QPixmap.fromImage(qt_image)
            
            scaled_pixmap = pixmap.scaled(
                self.video_display_width, self.video_display_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            original_frame = self.video_processor.get_current_frame()
            if original_frame is not None:
                orig_h, orig_w = original_frame.shape[:2]
                self.display_scale = scaled_pixmap.width() / orig_w * self.zoom_level
            
            self.video_label.setPixmap(scaled_pixmap)
    
    def draw_points_on_frame(self, frame):
        if not self.calculator:
            return frame
        
        points = self.calculator.get_points()
        
        for i, point in enumerate(points):
            color = (0, 255, 0) if i == len(points) - 1 else (0, 150, 255)
            cv2.circle(frame, (point.x, point.y), self.point_size, color, -1)
            cv2.circle(frame, (point.x, point.y), self.point_size + 2, (255, 255, 255), 2)
            
            label = f"{i+1}"
            label_offset = self.point_size + 7
            cv2.putText(frame, label, (point.x + label_offset, point.y - label_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, label, (point.x + label_offset, point.y - label_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1)
        
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            line_thickness = max(2, self.point_size // 4)
            cv2.line(frame, (p1.x, p1.y), (p2.x, p2.y), (255, 200, 0), line_thickness)
        
        return frame
    
    def start_point_selection(self):
        self.selecting_point = not self.selecting_point
        
        if self.selecting_point:
            self.select_point_btn.setText("Stop Selection")
            self.select_point_btn.setStyleSheet("background-color: #d32f2f; color: white;")
            self.status_bar.showMessage("Point selection mode active - Click on video to add points")
        else:
            self.select_point_btn.setText("Select Point")
            self.select_point_btn.setStyleSheet("")
            self.status_bar.showMessage("Point selection mode stopped")
    
    def video_label_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.selecting_point:
                self.video_label_clicked(event)
            elif self.zoom_level > 1.0:
                self.panning = True
                self.pan_start_x = event.pos().x()
                self.pan_start_y = event.pos().y()
                self.video_label.setCursor(Qt.CursorShape.ClosedHandCursor)
    
    def video_label_mouse_move(self, event):
        if self.panning and self.zoom_level > 1.0:
            frame = self.video_processor.get_current_frame()
            if frame is not None:
                frame_height, frame_width = frame.shape[:2]
                
                dx = event.pos().x() - self.pan_start_x
                dy = event.pos().y() - self.pan_start_y
                
                pan_sensitivity = 2
                self.zoom_offset_x -= int(dx * pan_sensitivity / self.zoom_level)
                self.zoom_offset_y -= int(dy * pan_sensitivity / self.zoom_level)
                
                max_offset_x = int(frame_width / 2 * (1 - 1/self.zoom_level))
                max_offset_y = int(frame_height / 2 * (1 - 1/self.zoom_level))
                
                self.zoom_offset_x = max(-max_offset_x, min(max_offset_x, self.zoom_offset_x))
                self.zoom_offset_y = max(-max_offset_y, min(max_offset_y, self.zoom_offset_y))
                
                self.pan_start_x = event.pos().x()
                self.pan_start_y = event.pos().y()
                
                self.display_frame()
    
    def video_label_mouse_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = False
            if self.zoom_level > 1.0:
                self.video_label.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.video_label.setCursor(Qt.CursorShape.ArrowCursor)
    
    def video_label_clicked(self, event):
        if not self.selecting_point or not self.video_loaded:
            return
        
        label_width = self.video_label.width()
        label_height = self.video_label.height()
        
        frame = self.video_processor.get_current_frame()
        if frame is None:
            return
        
        frame_height, frame_width = frame.shape[:2]
        
        pixmap = self.video_label.pixmap()
        if pixmap:
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()
            
            x_offset = (label_width - pixmap_width) // 2
            y_offset = (label_height - pixmap_height) // 2
            
            click_x = event.pos().x() - x_offset
            click_y = event.pos().y() - y_offset
            
            if 0 <= click_x < pixmap_width and 0 <= click_y < pixmap_height:
                if self.zoom_level > 1.0:
                    crop_w = int(frame_width / self.zoom_level)
                    crop_h = int(frame_height / self.zoom_level)
                    
                    center_x = frame_width // 2 + self.zoom_offset_x
                    center_y = frame_height // 2 + self.zoom_offset_y
                    
                    x1 = max(0, center_x - crop_w // 2)
                    y1 = max(0, center_y - crop_h // 2)
                    x2 = min(frame_width, x1 + crop_w)
                    y2 = min(frame_height, y1 + crop_h)
                    
                    x1 = max(0, x2 - crop_w)
                    y1 = max(0, y2 - crop_h)
                    
                    frame_x = int(x1 + (click_x / pixmap_width) * crop_w)
                    frame_y = int(y1 + (click_y / pixmap_height) * crop_h)
                else:
                    frame_x = int((click_x / pixmap_width) * frame_width)
                    frame_y = int((click_y / pixmap_height) * frame_height)
                
                current_frame = self.video_processor.current_frame_number
                index = self.calculator.add_point(frame_x, frame_y, current_frame)
                
                item_text = f"Point {index + 1}: Frame {current_frame}, ({frame_x}, {frame_y})"
                self.points_list.addItem(item_text)
                
                self.clear_last_btn.setEnabled(True)
                self.clear_all_btn.setEnabled(True)
                
                if len(self.calculator.get_points()) >= 2:
                    self.calculate_btn.setEnabled(True)
                
                self.status_bar.showMessage(f"Point {index + 1} added - Click to add more or press 'Stop Selection'")
                self.display_frame()
    
    def clear_last_point(self):
        if self.calculator and len(self.calculator.get_points()) > 0:
            self.calculator.remove_point(len(self.calculator.get_points()) - 1)
            self.points_list.takeItem(self.points_list.count() - 1)
            
            if len(self.calculator.get_points()) == 0:
                self.clear_last_btn.setEnabled(False)
                self.clear_all_btn.setEnabled(False)
                self.calculate_btn.setEnabled(False)
                self.export_btn.setEnabled(False)
                self.results_text.clear()
            elif len(self.calculator.get_points()) < 2:
                self.calculate_btn.setEnabled(False)
                self.export_btn.setEnabled(False)
                self.results_text.clear()
            
            self.display_frame()
            self.status_bar.showMessage("Last point removed")
    
    def clear_all_points(self):
        if self.calculator:
            self.calculator.clear_points()
        self.points_list.clear()
        self.results_text.clear()
        self.clear_last_btn.setEnabled(False)
        self.clear_all_btn.setEnabled(False)
        self.calculate_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        
        if self.selecting_point:
            self.selecting_point = False
            self.select_point_btn.setText("Select Point")
            self.select_point_btn.setStyleSheet("")
        
        self.display_frame()
        self.status_bar.showMessage("All points cleared")
    
    def calculate_speeds(self):
        if not self.calculator or len(self.calculator.get_points()) < 2:
            QMessageBox.warning(self, "Warning", "You must select at least 2 points!")
            return
        
        pixels = self.pixel_value
        um = self.um_value
        self.calculator.set_pixel_ratio(pixels, um)
        
        summary = self.calculator.get_summary_text()
        self.results_text.setPlainText(summary)
        self.export_btn.setEnabled(True)
        self.status_bar.showMessage("Calculations completed")
    
    def export_results(self):
        if not self.calculator or len(self.calculator.get_points()) < 2:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Results",
            "results.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                csv_content = self.calculator.export_to_csv()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Results successfully saved:\n{file_path}"
                )
                self.status_bar.showMessage("Results saved as CSV")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Save error: {str(e)}")
    
    def showEvent(self, event):
        super().showEvent(event)
        self.video_display_width = self.video_label.width()
        self.video_display_height = self.video_label.height()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        new_width = self.video_label.width()
        new_height = self.video_label.height()
        
        if new_width > 100 and new_height > 100:
            if new_width != self.video_display_width or new_height != self.video_display_height:
                self.video_display_width = new_width
                self.video_display_height = new_height
                
                if self.video_loaded and self.video_processor.get_current_frame() is not None:
                    self.display_frame()
    
    def keyPressEvent(self, event):
        key = event.key()
        
        if key == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showMaximized()
            else:
                self.showFullScreen()
            return
        elif key == Qt.Key.Key_Escape and self.isFullScreen():
            self.showMaximized()
            return
        
        if not self.video_loaded:
            super().keyPressEvent(event)
            return
        
        if key == Qt.Key.Key_Left:
            current = self.frame_slider.value()
            if current > 0:
                self.frame_slider.setValue(current - 1)
        elif key == Qt.Key.Key_Right:
            current = self.frame_slider.value()
            if current < self.frame_slider.maximum():
                self.frame_slider.setValue(current + 1)
        elif key == Qt.Key.Key_Home:
            self.frame_slider.setValue(0)
        elif key == Qt.Key.Key_End:
            self.frame_slider.setValue(self.frame_slider.maximum())
        elif key == Qt.Key.Key_PageUp:
            current = self.frame_slider.value()
            new_value = max(0, current - 10)
            self.frame_slider.setValue(new_value)
        elif key == Qt.Key.Key_PageDown:
            current = self.frame_slider.value()
            new_value = min(self.frame_slider.maximum(), current + 10)
            self.frame_slider.setValue(new_value)
        else:
            super().keyPressEvent(event)
    
    def zoom_in(self):
        if not self.video_loaded:
            return
        self.zoom_level = min(self.zoom_level * 1.5, 10.0)
        self.zoom_label.setText(f"Zoom: %{int(self.zoom_level * 100)}")
        if self.zoom_level > 1.0:
            self.video_label.setCursor(Qt.CursorShape.OpenHandCursor)
        self.display_frame()
        self.status_bar.showMessage(f"Zoom: %{int(self.zoom_level * 100)} - Drag to pan")
    
    def zoom_out(self):
        if not self.video_loaded:
            return
        self.zoom_level = max(self.zoom_level / 1.5, 1.0)
        if self.zoom_level == 1.0:
            self.zoom_offset_x = 0
            self.zoom_offset_y = 0
            self.video_label.setCursor(Qt.CursorShape.ArrowCursor)
        self.zoom_label.setText(f"Zoom: %{int(self.zoom_level * 100)}")
        self.display_frame()
        if self.zoom_level > 1.0:
            self.status_bar.showMessage(f"Zoom: %{int(self.zoom_level * 100)} - Drag to pan")
        else:
            self.status_bar.showMessage(f"Zoom: %{int(self.zoom_level * 100)}")
    
    def zoom_reset(self):
        self.zoom_level = 1.0
        self.zoom_offset_x = 0
        self.zoom_offset_y = 0
        self.zoom_label.setText(f"Zoom: %{int(self.zoom_level * 100)}")
        self.video_label.setCursor(Qt.CursorShape.ArrowCursor)
        if self.video_loaded:
            self.display_frame()
            self.status_bar.showMessage("Zoom reset")
    
    def wheelEvent(self, event):
        if self.video_loaded and event.angleDelta().y() != 0:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
    
    def show_about(self):
        about_text = """
<h2>Erytroscope</h2>
<p><b>Version 1.0</b></p>
<br>
<p>A professional video frame analysis application for precise point tracking and speed calculations.</p>
<br>
<p><b>Developed by:</b> Ibrahim Ünal</p>
<p><b>Email:</b> ibrahimunalofficial@gmail.com</p>
<p><b>Under the guidance of:</b> Prof. Dr. Ugur Aksu</p>
<br>
<p>© 2026 All rights reserved</p>
        """
        QMessageBox.about(self, "About Erytroscope", about_text)
    
    def closeEvent(self, event):
        self.video_processor.release()
        event.accept()
