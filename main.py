import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


app = QApplication(sys.argv)

cat = QLabel()

cat.setWindowFlags(
    Qt.WindowType.FramelessWindowHint |
    Qt.WindowType.WindowStaysOnTopHint |
    Qt.WindowType.Tool
)

cat.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

# Load cat image
pixmap = QPixmap("cat/cat1.png")

# Resize cat
pixmap = pixmap.scaled(
    120,
    120,
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation
)

cat.setPixmap(pixmap)
cat.resize(pixmap.size())

# Get screen size
screen = app.primaryScreen().availableGeometry()

# Put cat near the bottom-right of the screen
x = screen.width() - cat.width() - 50
y = screen.height() - cat.height() - 5

cat.move(x, y)

cat.show()

sys.exit(app.exec())