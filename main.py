import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, QTimer


app = QApplication(sys.argv)

# -----------------------------
# CAT WINDOW
# -----------------------------

cat = QLabel()

cat.setWindowFlags(
    Qt.WindowType.FramelessWindowHint |
    Qt.WindowType.WindowStaysOnTopHint |
    Qt.WindowType.Tool
)

cat.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


# -----------------------------
# LOAD FRAMES
# -----------------------------

image_files = [
    "cat/cat_walk_1.png",
    "cat/cat_walk_2.png",
    "cat/cat_walk_3.png"
]

frames = []

for file in image_files:

    pixmap = QPixmap(file)

    if pixmap.isNull():
        print("ERROR: Could not load:", file)
        continue

    pixmap = pixmap.scaled(
        120,
        120,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    frames.append(pixmap)

if not frames:
    print("No cat images loaded!")
    sys.exit()


# -----------------------------
# ANIMATION ORDER
# -----------------------------

frame_order = [0, 1, 2, 1]

current_frame = 0


# -----------------------------
# SCREEN
# -----------------------------

screen = app.primaryScreen().availableGeometry()

cat.resize(frames[0].size())


# -----------------------------
# START FROM RIGHT
# -----------------------------

x = screen.width() - cat.width() - 20

y = screen.height() - cat.height() - 5

# Cat initially faces LEFT
direction = -1

cat.setPixmap(frames[0])

cat.move(x, y)

cat.show()


# -----------------------------
# ANIMATE LEGS
# -----------------------------

def animate_cat():

    global current_frame

    current_frame += 1

    if current_frame >= len(frame_order):
        current_frame = 0

    frame_number = frame_order[current_frame]

    pixmap = frames[frame_number]

    # If moving RIGHT, flip cat
    if direction == 1:
        pixmap = pixmap.transformed(
            QTransform().scale(-1, 1)
        )

    cat.setPixmap(pixmap)


# -----------------------------
# MOVE CAT
# -----------------------------

def move_cat():

    global x
    global direction

    if direction == -1:

        # Move LEFT
        x -= 2

        if x <= 0:
            x = 0
            direction = 1

    else:

        # Move RIGHT
        x += 2

        if x >= screen.width() - cat.width():
            x = screen.width() - cat.width()
            direction = -1

    cat.move(x, y)


# -----------------------------
# TIMERS
# -----------------------------

animation_timer = QTimer()
animation_timer.timeout.connect(animate_cat)
animation_timer.start(150)


movement_timer = QTimer()
movement_timer.timeout.connect(move_cat)
movement_timer.start(30)


sys.exit(app.exec())