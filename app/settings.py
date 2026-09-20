import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QSpinBox
)


class SettingsWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("CATGuard 🐱")
        self.resize(400, 450)

        # Main layout
        layout = QVBoxLayout()

        # Title
        title = QLabel("🐱 CATGuard")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Manage your social media limits")
        layout.addWidget(subtitle)

        # -------------------------
        # Instagram
        # -------------------------

        instagram_layout = QHBoxLayout()

        instagram_check = QCheckBox("Instagram")
        instagram_check.setChecked(True)

        instagram_time = QSpinBox()
        instagram_time.setRange(1, 180)
        instagram_time.setValue(30)
        instagram_time.setSuffix(" min")

        instagram_layout.addWidget(instagram_check)
        instagram_layout.addWidget(instagram_time)

        layout.addLayout(instagram_layout)

        # -------------------------
        # YouTube
        # -------------------------

        youtube_layout = QHBoxLayout()

        youtube_check = QCheckBox("YouTube")
        youtube_check.setChecked(True)

        youtube_time = QSpinBox()
        youtube_time.setRange(1, 180)
        youtube_time.setValue(45)
        youtube_time.setSuffix(" min")

        youtube_layout.addWidget(youtube_check)
        youtube_layout.addWidget(youtube_time)

        layout.addLayout(youtube_layout)

        # -------------------------
        # Reddit
        # -------------------------

        reddit_layout = QHBoxLayout()

        reddit_check = QCheckBox("Reddit")

        reddit_time = QSpinBox()
        reddit_time.setRange(1, 180)
        reddit_time.setValue(30)
        reddit_time.setSuffix(" min")

        reddit_layout.addWidget(reddit_check)
        reddit_layout.addWidget(reddit_time)

        layout.addLayout(reddit_layout)

        # -------------------------
        # Cat option
        # -------------------------

        cat_check = QCheckBox("Show cat on desktop")
        cat_check.setChecked(True)

        layout.addWidget(cat_check)

        # -------------------------
        # Save button
        # -------------------------

        save_button = QPushButton("Save Settings")

        layout.addWidget(save_button)

        self.setLayout(layout)


# Run settings window
app = QApplication(sys.argv)

window = SettingsWindow()
window.show()

sys.exit(app.exec())