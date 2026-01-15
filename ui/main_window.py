from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSlider, QFileDialog, QGroupBox,
                             QStatusBar, QMessageBox, QDoubleSpinBox, QTextEdit,
                             QListWidget, QListWidgetItem)
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
        
        self.setWindowTitle("Frame Analiz Uygulaması")
        self.setMinimumSize(1900, 1300)
        
        self.init_ui()
        self.setStyleSheet(AppStyles.get_stylesheet())
        
        self.showMaximized()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        left_layout = QVBoxLayout()
        
        title_label = QLabel("Video Görüntüsü")
        title_label.setObjectName("title")
        left_layout.addWidget(title_label)
        
        self.video_label = QLabel()
        self.video_label.setObjectName("videoLabel")
        self.video_label.setMinimumSize(800, 600)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setText("Video yüklemek için 'Video Yükle' butonuna tıklayın")
        self.video_label.setStyleSheet(f"""
            QLabel {{
                background-color: {AppStyles.TEXT_BLACK};
                color: white;
                font-size: 16px;
            }}
        """)
        self.video_label.mousePressEvent = self.video_label_clicked
        self.video_label.setScaledContents(False)
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
        
        main_layout.addLayout(left_layout, 75)
        
        right_layout = QVBoxLayout()
        
        video_group = QGroupBox("Video İşlemleri")
        video_group.setMaximumHeight(150)
        video_group_layout = QVBoxLayout()
        
        self.load_video_btn = QPushButton("Video Yükle")
        self.load_video_btn.clicked.connect(self.load_video)
        video_group_layout.addWidget(self.load_video_btn)
        
        self.video_info_label = QLabel("Video bilgisi yok")
        self.video_info_label.setWordWrap(True)
        video_group_layout.addWidget(self.video_info_label)
        
        video_group.setLayout(video_group_layout)
        right_layout.addWidget(video_group)
        
        settings_group = QGroupBox("Ölçüm Ayarları")
        settings_group.setMaximumHeight(150)
        settings_layout = QVBoxLayout()
        
        ratio_layout = QHBoxLayout()
        ratio_layout.addWidget(QLabel("Pixel:"))
        self.pixel_input = QDoubleSpinBox()
        self.pixel_input.setRange(1, 10000)
        self.pixel_input.setValue(546)
        self.pixel_input.setDecimals(2)
        ratio_layout.addWidget(self.pixel_input)
        settings_layout.addLayout(ratio_layout)
        
        um_layout = QHBoxLayout()
        um_layout.addWidget(QLabel("µm:"))
        self.um_input = QDoubleSpinBox()
        self.um_input.setRange(1, 100000)
        self.um_input.setValue(1000)
        self.um_input.setDecimals(2)
        um_layout.addWidget(self.um_input)
        settings_layout.addLayout(um_layout)
        
        ratio_info = QLabel("546 pixel = 1000 µm")
        ratio_info.setStyleSheet("color: #666; font-size: 12px; font-style: italic;")
        settings_layout.addWidget(ratio_info)
        
        settings_group.setLayout(settings_layout)
        right_layout.addWidget(settings_group)
        
        points_group = QGroupBox("Nokta Seçimi")
        points_layout = QVBoxLayout()
        
        self.select_point_btn = QPushButton("Nokta Seç")
        self.select_point_btn.setEnabled(False)
        self.select_point_btn.clicked.connect(self.start_point_selection)
        points_layout.addWidget(self.select_point_btn)
        
        self.points_list = QListWidget()
        self.points_list.setMinimumHeight(120)
        self.points_list.setMaximumHeight(200)
        points_layout.addWidget(self.points_list)
        
        points_buttons_layout = QHBoxLayout()
        self.clear_last_btn = QPushButton("Son Noktayı Sil")
        self.clear_last_btn.setEnabled(False)
        self.clear_last_btn.clicked.connect(self.clear_last_point)
        points_buttons_layout.addWidget(self.clear_last_btn)
        
        self.clear_all_btn = QPushButton("Tümünü Temizle")
        self.clear_all_btn.setEnabled(False)
        self.clear_all_btn.clicked.connect(self.clear_all_points)
        points_buttons_layout.addWidget(self.clear_all_btn)
        points_layout.addLayout(points_buttons_layout)
        
        points_group.setLayout(points_layout)
        right_layout.addWidget(points_group)
        
        calc_group = QGroupBox("Hesaplama")
        calc_layout = QVBoxLayout()
        
        self.calculate_btn = QPushButton("Hesapla")
        self.calculate_btn.setEnabled(False)
        self.calculate_btn.clicked.connect(self.calculate_speeds)
        calc_layout.addWidget(self.calculate_btn)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(200)
        self.results_text.setPlaceholderText("Sonuçlar burada görünecek...")
        calc_layout.addWidget(self.results_text)
        
        self.export_btn = QPushButton("Sonuçları CSV Olarak Kaydet")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_results)
        calc_layout.addWidget(self.export_btn)
        
        calc_group.setLayout(calc_layout)
        right_layout.addWidget(calc_group)
        
        right_layout.addStretch()
        
        main_layout.addLayout(right_layout, 25)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")
        
    def load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Video Seç", 
            "", 
            "Video Dosyaları (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_path:
            try:
                if self.video_processor.load_video(file_path):
                    self.video_loaded = True
                    info = self.video_processor.get_video_info()
                    
                    pixels = self.pixel_input.value()
                    um = self.um_input.value()
                    self.calculator = SpeedCalculator(info['fps'], um / pixels)
                    
                    self.video_info_label.setText(
                        f"FPS: {info['fps']}\n"
                        f"Toplam Frame: {info['total_frames']}\n"
                        f"Çözünürlük: {info['width']}x{info['height']}\n"
                        f"Süre: {info['duration']:.2f} saniye"
                    )
                    
                    self.frame_slider.setMaximum(info['total_frames'] - 1)
                    self.frame_slider.setValue(0)
                    self.frame_slider.setEnabled(True)
                    self.select_point_btn.setEnabled(True)
                    
                    self.clear_all_points()
                    
                    self.display_frame()
                    self.status_bar.showMessage(f"Video yüklendi: {Path(file_path).name}")
                else:
                    QMessageBox.critical(self, "Hata", "Video yüklenemedi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Video yükleme hatası: {str(e)}")
    
    def slider_changed(self, value):
        if self.video_loaded:
            self.video_processor.get_frame(value)
            self.display_frame()
            self.frame_label.setText(f"{value} / {self.video_processor.total_frames - 1}")
    
    def display_frame(self):
        frame = self.video_processor.get_current_frame()
        if frame is not None:
            display_frame = frame.copy()
            display_frame = self.draw_points_on_frame(display_frame)
            
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            pixmap = QPixmap.fromImage(qt_image)
            
            available_width = self.video_label.width()
            available_height = self.video_label.height()
            
            if available_width > 100 and available_height > 100:
                scaled_pixmap = pixmap.scaled(
                    available_width, available_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.display_scale = scaled_pixmap.width() / w
                self.video_label.setPixmap(scaled_pixmap)
    
    def draw_points_on_frame(self, frame):
        if not self.calculator:
            return frame
        
        points = self.calculator.get_points()
        
        for i, point in enumerate(points):
            color = (0, 255, 0) if i == len(points) - 1 else (0, 150, 255)
            cv2.circle(frame, (point.x, point.y), 8, color, -1)
            cv2.circle(frame, (point.x, point.y), 10, (255, 255, 255), 2)
            
            label = f"{i+1}"
            cv2.putText(frame, label, (point.x + 15, point.y - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, label, (point.x + 15, point.y - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1)
        
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            cv2.line(frame, (p1.x, p1.y), (p2.x, p2.y), (255, 200, 0), 2)
        
        return frame
    
    def start_point_selection(self):
        self.selecting_point = True
        self.select_point_btn.setText("🎯 Videoda bir nokta tıklayın...")
        self.select_point_btn.setEnabled(False)
        self.status_bar.showMessage("Video üzerinde bir nokta seçin")
    
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
                frame_x = int((click_x / pixmap_width) * frame_width)
                frame_y = int((click_y / pixmap_height) * frame_height)
                
                current_frame = self.video_processor.current_frame_number
                index = self.calculator.add_point(frame_x, frame_y, current_frame)
                
                item_text = f"Nokta {index + 1}: Frame {current_frame}, ({frame_x}, {frame_y})"
                self.points_list.addItem(item_text)
                
                self.clear_last_btn.setEnabled(True)
                self.clear_all_btn.setEnabled(True)
                
                if len(self.calculator.get_points()) >= 2:
                    self.calculate_btn.setEnabled(True)
                
                self.selecting_point = False
                self.select_point_btn.setText("🎯 Nokta Seç")
                self.select_point_btn.setEnabled(True)
                self.status_bar.showMessage(f"Nokta {index + 1} eklendi")
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
            self.status_bar.showMessage("Son nokta silindi")
    
    def clear_all_points(self):
        if self.calculator:
            self.calculator.clear_points()
        self.points_list.clear()
        self.results_text.clear()
        self.clear_last_btn.setEnabled(False)
        self.clear_all_btn.setEnabled(False)
        self.calculate_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.display_frame()
        self.status_bar.showMessage("Tüm noktalar temizlendi")
    
    def calculate_speeds(self):
        if not self.calculator or len(self.calculator.get_points()) < 2:
            QMessageBox.warning(self, "Uyarı", "En az 2 nokta seçmelisiniz!")
            return
        
        pixels = self.pixel_input.value()
        um = self.um_input.value()
        self.calculator.set_pixel_ratio(pixels, um)
        
        summary = self.calculator.get_summary_text()
        self.results_text.setPlainText(summary)
        self.export_btn.setEnabled(True)
        self.status_bar.showMessage("Hesaplamalar tamamlandı")
    
    def export_results(self):
        if not self.calculator or len(self.calculator.get_points()) < 2:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sonuçları Kaydet",
            "sonuclar.csv",
            "CSV Dosyaları (*.csv)"
        )
        
        if file_path:
            try:
                csv_content = self.calculator.export_to_csv()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                
                QMessageBox.information(
                    self,
                    "Başarılı",
                    f"Sonuçlar başarıyla kaydedildi:\n{file_path}"
                )
                self.status_bar.showMessage("Sonuçlar CSV olarak kaydedildi")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kayıt hatası: {str(e)}")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
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
    
    def closeEvent(self, event):
        self.video_processor.release()
        event.accept()
