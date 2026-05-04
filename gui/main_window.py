from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)

from core.batch_runner import BatchRunner
from utils.file_helper import collect_images, collect_videos
from utils.logger import AppLogger


class Worker(QThread):
    log = Signal(str)
    progress = Signal(int, int)
    done = Signal()

    def __init__(self, videos, images, output_dir, settings):
        super().__init__()
        self.runner = BatchRunner(self.log.emit)
        self.videos = videos
        self.images = images
        self.output_dir = output_dir
        self.settings = settings

    def run(self):
        self.runner.process(self.videos, self.images, self.output_dir, self.settings, self.progress.emit)
        self.done.emit()

    def stop(self):
        self.runner.stop()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Video Shuffle + Image Compositor")
        self.resize(980, 700)
        self._build_ui()
        self.worker: Worker | None = None

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        self.video_list = QListWidget()
        layout.addWidget(QLabel("Danh sách video"))
        layout.addWidget(self.video_list)

        row = QHBoxLayout()
        btn_add_files = QPushButton("Add Files")
        btn_add_folder = QPushButton("Add Folder")
        btn_remove = QPushButton("Remove")
        row.addWidget(btn_add_files); row.addWidget(btn_add_folder); row.addWidget(btn_remove)
        layout.addLayout(row)

        self.image_label = QLabel("Chưa chọn ảnh/thư mục ảnh")
        self.output_label = QLabel("Output: auto")
        layout.addWidget(self.image_label)
        layout.addWidget(self.output_label)

        row2 = QHBoxLayout()
        btn_image = QPushButton("Chọn ảnh/thư mục ảnh")
        btn_output = QPushButton("Chọn output")
        row2.addWidget(btn_image); row2.addWidget(btn_output)
        layout.addLayout(row2)

        self.scene_spin = QSpinBox(); self.scene_spin.setRange(1, 100); self.scene_spin.setValue(27)
        self.overlap_spin = QSpinBox(); self.overlap_spin.setRange(1, 20); self.overlap_spin.setValue(5)
        self.focus_combo = QComboBox(); self.focus_combo.addItems(["center", "top", "bottom"])
        self.random_combo = QComboBox(); self.random_combo.addItems(["keep_first", "full"])
        self.auto_open = QCheckBox("Auto open output folder")

        for w, lbl in [
            (self.scene_spin, "Scene sensitivity"),
            (self.overlap_spin, "Overlap %"),
            (self.focus_combo, "Image crop focus"),
            (self.random_combo, "Random mode"),
        ]:
            layout.addWidget(QLabel(lbl)); layout.addWidget(w)
        layout.addWidget(self.auto_open)

        self.progress = QProgressBar(); layout.addWidget(self.progress)
        self.logs = QTextEdit(); self.logs.setReadOnly(True); layout.addWidget(self.logs)

        row3 = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_open = QPushButton("Open Output Folder")
        row3.addWidget(self.btn_start); row3.addWidget(self.btn_stop); row3.addWidget(self.btn_open)
        layout.addLayout(row3)

        btn_add_files.clicked.connect(self.add_files)
        btn_add_folder.clicked.connect(self.add_folder)
        btn_remove.clicked.connect(lambda: self.video_list.takeItem(self.video_list.currentRow()))
        btn_image.clicked.connect(self.pick_images)
        btn_output.clicked.connect(self.pick_output)
        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_open.clicked.connect(self.open_output)

        self.image_path: Path | None = None
        self.output_dir: Path | None = None

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Video files")
        for p in collect_videos([Path(f) for f in files]):
            self.video_list.addItem(str(p))

    def add_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Video folder")
        if d:
            for p in collect_videos([Path(d)]):
                self.video_list.addItem(str(p))

    def pick_images(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn 1 ảnh (Cancel để chọn folder)")
        if path:
            self.image_path = Path(path)
        else:
            d = QFileDialog.getExistingDirectory(self, "Chọn thư mục ảnh")
            if d:
                self.image_path = Path(d)
        if self.image_path:
            self.image_label.setText(str(self.image_path))

    def pick_output(self):
        d = QFileDialog.getExistingDirectory(self, "Chọn output folder")
        if d:
            self.output_dir = Path(d)
            self.output_label.setText(f"Output: {d}")

    def start(self):
        videos = [Path(self.video_list.item(i).text()) for i in range(self.video_list.count())]
        if not videos:
            return QMessageBox.warning(self, "Thiếu dữ liệu", "Chưa có video.")
        if not self.image_path:
            return QMessageBox.warning(self, "Thiếu dữ liệu", "Chưa chọn ảnh.")
        images = collect_images(self.image_path)
        if not images:
            return QMessageBox.warning(self, "Lỗi ảnh", "Không tìm thấy ảnh hợp lệ.")

        settings = {
            "scene_sensitivity": float(self.scene_spin.value()),
            "overlap_percent": self.overlap_spin.value(),
            "crop_focus": self.focus_combo.currentText(),
            "random_mode": self.random_combo.currentText(),
            "cleanup_temp": True,
        }
        self.logs.clear()
        self.worker = Worker(videos, images, self.output_dir, settings)
        self.worker.log.connect(lambda m: self.logs.append(m))
        self.worker.progress.connect(self._on_progress)
        self.worker.done.connect(self._done)
        self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()

    def _on_progress(self, done, total):
        self.progress.setValue(int(done / total * 100))

    def _done(self):
        QMessageBox.information(self, "Xong", "Xử lý hoàn tất.")

    def open_output(self):
        if self.output_dir and self.output_dir.exists():
            import os
            os.startfile(str(self.output_dir))
