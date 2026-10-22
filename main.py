import sys
import os
import json
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer

from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, QTimer, QObject, Signal


# =========================================================
# APPLICATION
# =========================================================

app = QApplication(sys.argv)


# =========================================================
# QT SIGNALS
# =========================================================

class CATGuardSignals(QObject):
    make_angry = Signal(str)
    make_normal = Signal()


signals = CATGuardSignals()


# =========================================================
# PROJECT PATH
# =========================================================

base_dir = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# CAT WINDOW
# =========================================================

cat = QLabel()

cat.setWindowFlags(
    Qt.WindowType.FramelessWindowHint |
    Qt.WindowType.WindowStaysOnTopHint |
    Qt.WindowType.Tool
)

cat.setAttribute(
    Qt.WidgetAttribute.WA_TranslucentBackground
)


# =========================================================
# LOAD WALKING FRAMES
# =========================================================

image_files = [
    os.path.join(base_dir, "cat", "cat_walk_1.png"),
    os.path.join(base_dir, "cat", "cat_walk_2.png"),
    os.path.join(base_dir, "cat", "cat_walk_3.png")
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

    print("ERROR: No walking frames loaded!")

    sys.exit()


print("CATGuard: Loaded", len(frames), "walking frames")


# =========================================================
# LOAD ANGRY CAT
# =========================================================

angry_file = os.path.join(
    base_dir,
    "cat",
    "cat_angry.png"
)

angry_pixmap = QPixmap(angry_file)

if angry_pixmap.isNull():

    print("ERROR: Could not load angry cat:", angry_file)

else:

    angry_pixmap = angry_pixmap.scaled(
        120,
        120,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    print("CATGuard: Angry cat loaded")


# =========================================================
# ANIMATION SETTINGS
# =========================================================

frame_order = [0, 1, 2, 1]

current_frame = 0

is_angry = False

angry_site = None


# =========================================================
# SCREEN AND POSITION
# =========================================================

screen = app.primaryScreen().availableGeometry()

cat_width = 120
cat_height = 120

cat.resize(cat_width, cat_height)

x = screen.right() - cat_width

y = screen.bottom() - cat_height + 1

direction = -1


# =========================================================
# INITIAL CAT
# =========================================================

cat.setPixmap(frames[frame_order[current_frame]])

cat.move(x, y)

cat.show()


# =========================================================
# WALKING TIMER
# =========================================================

walk_timer = QTimer()


# =========================================================
# MAKE CAT ANGRY
# =========================================================

def make_cat_angry(site):

    global is_angry
    global angry_site

    if angry_pixmap.isNull():

        print("ERROR: Angry image is unavailable")

        return

    is_angry = True

    angry_site = site

    walk_timer.stop()

    cat.setPixmap(angry_pixmap)

    cat.show()

    print("CATGuard: Cat is angry because of", site)


# =========================================================
# MAKE CAT NORMAL
# =========================================================

def make_cat_normal():

    global is_angry
    global angry_site

    is_angry = False

    angry_site = None

    cat.setPixmap(
        frames[frame_order[current_frame]]
    )

    cat.show()

    walk_timer.start(100)

    print("CATGuard: Cat returned to normal walking")


# =========================================================
# CONNECT QT SIGNALS
# =========================================================

signals.make_angry.connect(make_cat_angry)

signals.make_normal.connect(make_cat_normal)


# =========================================================
# WALK CAT
# =========================================================

def walk_cat():

    global current_frame
    global x
    global direction

    if is_angry:
        return

    current_frame += 1

    if current_frame >= len(frame_order):
        current_frame = 0

    pixmap = frames[frame_order[current_frame]]

    if direction == -1:

        cat.setPixmap(pixmap)

    else:

        cat.setPixmap(
            pixmap.transformed(
                QTransform().scale(-1, 1)
            )
        )

    step = 3

    if direction == -1:

        x -= step

        if x <= screen.left():

            x = screen.left()

            direction = 1

    else:

        x += step

        if x >= screen.right() - cat_width + 1:

            x = screen.right() - cat_width + 1

            direction = -1

    cat.move(x, y)


walk_timer.timeout.connect(walk_cat)

walk_timer.start(100)


# =========================================================
# HTTP SERVER
# =========================================================

class CATGuardRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        try:

            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            data = json.loads(body.decode("utf-8"))

            action = data.get("action", "alert")

            site = data.get("site", "unknown")

            if self.path == "/alert" and action == "alert":

                print("CATGuard: Limit reached on", site)

                signals.make_angry.emit(site)

            elif self.path == "/normal":

                print("CATGuard: Normal state requested")

                signals.make_normal.emit()

            else:

                self.send_response(404)

                self.end_headers()

                return

            self.send_response(200)

            self.send_header("Content-Type", "application/json")

            self.send_header("Access-Control-Allow-Origin", "*")

            self.end_headers()

            self.wfile.write(
                json.dumps({
                    "status": "success",
                    "action": action,
                    "site": site
                }).encode("utf-8")
            )

        except Exception as error:

            print("CATGuard server error:", error)

            self.send_response(500)

            self.end_headers()

    def do_OPTIONS(self):

        self.send_response(200)

        self.send_header("Access-Control-Allow-Origin", "*")

        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        self.end_headers()

    def log_message(self, format, *args):

        return


# =========================================================
# START LOCAL SERVER
# =========================================================

def start_server():

    try:

        server = HTTPServer(
            ("127.0.0.1", 5000),
            CATGuardRequestHandler
        )

        print("CATGuard: Local server started")

        print("CATGuard: Waiting for Chrome alerts...")

        server.serve_forever()

    except Exception as error:

        print("CATGuard server failed:", error)


server_thread = threading.Thread(
    target=start_server,
    daemon=True
)

server_thread.start()


# =========================================================
# START APPLICATION
# =========================================================

sys.exit(app.exec())