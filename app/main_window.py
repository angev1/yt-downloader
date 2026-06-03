# from .downloader import build_ydl_opts, get_text_dir, get_file_type, get_video_quality, is_valid_youtube_url

from PySide6.QtWidgets import (QMainWindow, QLabel, QPushButton, QWidget,
                                QVBoxLayout, QHBoxLayout, QLineEdit, QFileDialog, QComboBox,
                                QProgressBar, QMessageBox)


class MainWindow(QMainWindow):
    def __init__(self, project_root):
        super().__init__()
        self.project_root = project_root
        self.thread = None
        self.has_error = False
        self.close_requested = False
        self.setWindowTitle('YouTube Downloader')
        self.setGeometry(700, 330, 560, 280)
        self.setMinimumSize(560, 280)
        self.initUI()

    def initUI(self):
        from .downloader import get_text_dir, get_file_type, get_video_quality
        self.container = QWidget()
        self.container.setObjectName("container")
        self.setCentralWidget(self.container)

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(12)

        title = QLabel("YouTube Downloader")
        title.setObjectName("title")
        main_layout.addWidget(title)

        self.line_url = QLineEdit()
        self.line_url.setObjectName("urlInput")
        self.line_url.setPlaceholderText("Paste YouTube URL here...")
        self.line_url.setFixedHeight(48)
        main_layout.addWidget(self.line_url)

        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(8)

        self.line_dir = QLineEdit()
        self.line_dir.setObjectName("dirInput")
        self.line_dir.setPlaceholderText("Save directory...")
        self.line_dir.setFixedHeight(48)
        self.line_dir.setText(get_text_dir(self.project_root))
        dir_layout.addWidget(self.line_dir)

        self.btn_browse = QPushButton("Browse")
        self.btn_browse.setObjectName("browseButton")
        self.btn_browse.setFixedSize(90, 48)
        self.btn_browse.clicked.connect(self.press_button_path)
        dir_layout.addWidget(self.btn_browse)

        main_layout.addLayout(dir_layout)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        self.combobox = QComboBox()
        self.combobox.setObjectName("formatCombo")
        self.combobox.addItems(get_file_type(self.project_root))
        self.combobox.setFixedHeight(48)
        self.combobox.setMinimumWidth(90)
        controls_layout.addWidget(self.combobox)

        self.combobox2 = QComboBox()
        self.combobox2.setObjectName("qualityCombo")
        self.combobox2.addItems(["The best", "1080", "720", "480", "360", "144"])
        self.combobox2.setFixedHeight(48)
        self.combobox2.setMinimumWidth(90)
        controls_layout.addWidget(self.combobox2)

        controls_layout.addStretch()

        self.button = QPushButton("Download")
        self.button.setObjectName("downloadButton")
        self.button.setFixedHeight(48)
        self.button.setMinimumWidth(140)
        self.button.clicked.connect(self.start_thread)
        controls_layout.addWidget(self.button)

        main_layout.addLayout(controls_layout)

        self.label_status = QLabel("")
        self.label_status.setObjectName("statusLabel")
        main_layout.addWidget(self.label_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

    def press_button_path(self):
        path = QFileDialog.getExistingDirectory(self, 'Select a directory')
        if path:
            self.line_dir.setText(path)

    def start_thread(self):
        from .downloader import get_text_dir, get_file_type, get_video_quality, is_valid_youtube_url, build_ydl_opts
        if self.thread is not None and self.thread.isRunning():
            return

        url = self.line_url.text().strip()
        directory = self.line_dir.text()
        format_file = self.combobox.currentText()
        video_quality = self.combobox2.currentText()

        if not is_valid_youtube_url(url):
            self.label_status.setText("Invalid YouTube URL.")
            self.show_error("Invalid YouTube URL.")
            return 

        self.label_status.setText("Download...")
        self.button.setEnabled(False)

        thread = build_ydl_opts(format_file, self.project_root, video_quality, directory, url)
        self.thread = thread
        self.has_error = False
        self.close_requested = False
        thread.error_signal.connect(self.on_error)
        thread.finished.connect(self.on_finished)
        thread.finished.connect(lambda: self.clear_thread(thread))
        thread.finished.connect(thread.deleteLater)
        thread.progress.connect(self.progress_bar.setValue)
        thread.start()

    def on_finished(self):
        self.button.setEnabled(True)
        if not self.has_error:
            self.progress_bar.setValue(100)
            self.label_status.setText("Completed.")
        if self.close_requested:
            self.close()

    def clear_thread(self, thread):
        if self.thread is thread:
            self.thread = None

    def closeEvent(self, event):
        if self.thread is not None and self.thread.isRunning():
            self.close_requested = True
            self.thread.requestInterruption()
            self.label_status.setText("Stopping download...")
            event.ignore()
            return

        super().closeEvent(event)

    def show_error(self, message):
        QMessageBox.critical(self, "Download Error", message)

    def on_error(self, message):
        self.has_error = True
        self.label_status.setText(message)
        if self.close_requested and message == "Download cancelled.":
            return
        self.show_error(message)
