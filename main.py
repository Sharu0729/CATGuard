import sys
import os
import json
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer

from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, QTimer


# =========================================================
# APPLICATION
# =========================================================

app = QApplication(sys.argv)


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
# PROJECT PATH
# =========================================================

base_dir = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# LOAD WALKING FRAMES
# =========================================================

image_files = [
    os.path.join(
        base_dir,
        "cat",
        "cat_walk_1.png"
    ),

    os.path.join(
        base_dir,
        "cat",
        "cat_walk_2.png"
    ),

    os.path.join(
        base_dir,
        "cat",
        "cat_walk_3.png"
    )
]

frames = []


for file in image_files:

    pixmap = QPixmap(file)

    if pixmap.isNull():

        print(
            "ERROR: Could not load:",
            file
        )

        continue

    pixmap = pixmap.scaled(
        120,
        120,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    frames.append(pixmap)


if len(frames) == 0:

    print(
        "ERROR: No cat walking frames loaded!"
    )

    sys.exit()


print(
    "CATGuard: Loaded",
    len(frames),
    "walking frames"
)


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

    print(
        "ERROR: Could not load angry cat:",
        angry_file
    )

else:

    angry_pixmap = angry_pixmap.scaled(
        120,
        120,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    print(
        "CATGuard: Angry cat loaded"
    )


# =========================================================
# WALKING ANIMATION ORDER
# =========================================================

frame_order = [
    0,
    1,
    2,
    1
]

current_frame = 0


# =========================================================
# SCREEN
# =========================================================

screen = app.primaryScreen().availableGeometry()

cat_width = 120
cat_height = 120

cat.resize(
    cat_width,
    cat_height
)


# =========================================================
# INITIAL POSITION
# =========================================================

x = screen.right() - cat_width

y = screen.bottom() - cat_height + 1


# =========================================================
# DIRECTION
# =========================================================

# -1 = LEFT
# +1 = RIGHT

direction = -1


# =========================================================
# CAT STATE
# =========================================================

is_angry = False


# =========================================================
# INITIAL CAT
# =========================================================

cat.setPixmap(
    frames[frame_order[current_frame]]
)

cat.move(
    x,
    y
)

cat.show()


# =========================================================
# MAKE CAT ANGRY
# =========================================================

def make_cat_angry():

    global is_angry

    if is_angry:

        print(
            "CATGuard: Cat is already angry."
        )

        return

    if angry_pixmap.isNull():

        print(
            "ERROR: Angry cat image is not available."
        )

        return

    is_angry = True

    # Stop walking
    walk_timer.stop()

    # Show angry cat
    cat.setPixmap(
        angry_pixmap
    )

    print(
        "CATGuard: Cat is angry!"
    )


# =========================================================
# WALK CAT
# =========================================================

def walk_cat():

    global current_frame
    global x
    global direction

    # -----------------------------------------
    # DO NOT WALK WHEN ANGRY
    # -----------------------------------------

    if is_angry:
        return


    # -----------------------------------------
    # CHANGE WALKING FRAME
    # -----------------------------------------

    current_frame += 1

    if current_frame >= len(frame_order):

        current_frame = 0

    frame_number = frame_order[
        current_frame
    ]

    pixmap = frames[
        frame_number
    ]


    # -----------------------------------------
    # FACE DIRECTION
    # -----------------------------------------

    if direction == -1:

        # Face LEFT

        cat.setPixmap(
            pixmap
        )

    else:

        # Face RIGHT

        flipped_pixmap = pixmap.transformed(
            QTransform().scale(
                -1,
                1
            )
        )

        cat.setPixmap(
            flipped_pixmap
        )


    # -----------------------------------------
    # MOVE CAT
    # -----------------------------------------

    step = 3


    if direction == -1:

        # Move LEFT

        x -= step


        # LEFT EDGE

        if x <= screen.left():

            x = screen.left()

            direction = 1


    else:

        # Move RIGHT

        x += step


        # RIGHT EDGE

        if x >= screen.right() - cat_width + 1:

            x = (
                screen.right()
                - cat_width
                + 1
            )

            direction = -1


    # -----------------------------------------
    # UPDATE POSITION
    # -----------------------------------------

    cat.move(
        x,
        y
    )


# =========================================================
# HTTP SERVER
# =========================================================

class CATGuardRequestHandler(
    BaseHTTPRequestHandler
):

    def do_POST(self):

        # -------------------------------------
        # ONLY ACCEPT /alert
        # -------------------------------------

        if self.path != "/alert":

            self.send_response(404)

            self.end_headers()

            return


        # -------------------------------------
        # READ DATA
        # -------------------------------------

        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            )

            data = json.loads(
                body.decode("utf-8")
            )

            site = data.get(
                "site",
                "unknown"
            )


            print(
                "CATGuard: Alert received from:",
                site
            )


            # ---------------------------------
            # CHANGE CAT ON QT MAIN THREAD
            # ---------------------------------

            QTimer.singleShot(
                0,
                make_cat_angry
            )


            # ---------------------------------
            # SEND SUCCESS RESPONSE
            # ---------------------------------

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.end_headers()

            response = {
                "status": "success",
                "message": "Cat became angry",
                "site": site
            }

            self.wfile.write(
                json.dumps(
                    response
                ).encode("utf-8")
            )


        except Exception as error:

            print(
                "CATGuard server error:",
                error
            )

            self.send_response(500)

            self.end_headers()


    # -----------------------------------------
    # KEEP TERMINAL CLEAN
    # -----------------------------------------

    def log_message(
        self,
        format,
        *args
    ):

        return


# =========================================================
# START LOCAL SERVER
# =========================================================

def start_server():

    try:

        server = HTTPServer(
            (
                "127.0.0.1",
                5000
            ),
            CATGuardRequestHandler
        )

        print(
            "CATGuard: Local server started"
        )

        print(
            "CATGuard: Waiting for Chrome alerts..."
        )

        server.serve_forever()


    except Exception as error:

        print(
            "CATGuard server failed:",
            error
        )


server_thread = threading.Thread(
    target=start_server,
    daemon=True
)

server_thread.start()


# =========================================================
# WALKING TIMER
# =========================================================

walk_timer = QTimer()

walk_timer.timeout.connect(
    walk_cat
)

walk_timer.start(100)


# =========================================================
# START APPLICATION
# =========================================================

sys.exit(
    app.exec()
)