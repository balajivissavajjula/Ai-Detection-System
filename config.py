
# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# CENTRAL CONFIGURATION
#
# CLEAN / SEPARATE STATE VERSION
#
# MODELS
# ------------------------------------------------------------
# 1. book_phone
#       0 = book
#       1 = phone
#
# 2. exam_behavior
#       0 = cheating
#       1 = normal
#       2 = cheat_paper
#       3 = look_around
#       4 = use_phone
#
# 3. paper_face_hand
#       0 = paper
#       1 = Face
#       2 = fist
#       3 = index_left
#       4 = index_right
#       5 = open_palm
#       6 = point
#       7 = thumbs_down
#       8 = thumbs_up
#
# 4. object
#       0 = calculator
#       1 = earphone
#       2 = sunglasses
#       3 = watch
#
# IMPORTANT
# ------------------------------------------------------------
# Behavior labels and physical object labels are kept separate.
#
# use_phone  != phone_detected
# cheat_paper != paper_detected
#
# Physical object flags are generated only by the model that
# actually owns that physical object.
# ============================================================

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODELS_DIR = BASE_DIR / "models"
KNOWN_FACES_DIR = BASE_DIR / "known_faces"

SCREENSHOT_DIR = BASE_DIR / "screenshots"
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"


# ============================================================
# CREATE DIRECTORIES
# ============================================================

for directory in (
    MODELS_DIR,
    KNOWN_FACES_DIR,
    SCREENSHOT_DIR,
    LOG_DIR,
    REPORT_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# CAMERA
# ============================================================

CAMERA_SOURCE = "phone"

CAMERA_INDEX = 0

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


# ============================================================
# ANDROID IP WEBCAM
# ============================================================

PHONE_IP = "192.168.55.102"

PHONE_PORT = 8080

PHONE_STREAM_URL = (
    f"http://{PHONE_IP}:{PHONE_PORT}/video"
)


# ============================================================
# YOLO MODEL PATHS
# ============================================================

BOOK_PHONE_MODEL = (
    MODELS_DIR
    / "book_phone"
    / "best.pt"
)

EXAM_BEHAVIOR_MODEL = (
    MODELS_DIR
    / "exam_behavior"
    / "best.pt"
)

PAPER_FACE_HAND_MODEL = (
    MODELS_DIR
    / "_PAPER_FACE_HAND_DATASET"
    / "best.pt"
)

OBJECT_MODEL = (
    MODELS_DIR
    / "object"
    / "best.pt"
)


# ============================================================
# OLD / BACKUP MODEL
# ============================================================

OLD_OBJECT_MODEL = (
    MODELS_DIR
    / "best_objects.pt"
)


# ============================================================
# MODEL CLASSES
# ============================================================

BOOK_PHONE_CLASSES = {
    0: "book",
    1: "phone",
}


EXAM_BEHAVIOR_CLASSES = {
    0: "cheating",
    1: "normal",
    2: "cheat_paper",
    3: "look_around",
    4: "use_phone",
}


PAPER_FACE_HAND_CLASSES = {
    0: "paper",
    1: "Face",
    2: "fist",
    3: "index_left",
    4: "index_right",
    5: "open_palm",
    6: "point",
    7: "thumbs_down",
    8: "thumbs_up",
}


OBJECT_CLASSES = {
    0: "calculator",
    1: "earphone",
    2: "sunglasses",
    3: "watch",
}


# ============================================================
# YOLO GENERAL SETTINGS
# ============================================================

YOLO_CONFIDENCE = 0.30

YOLO_IMAGE_SIZE = 416

YOLO_INFERENCE_SIZE = 320

YOLO_MAX_DETECTIONS = 50

YOLO_HALF = False

YOLO_DEVICE = "cpu"


# ============================================================
# MODEL-SPECIFIC CONFIDENCE
# ============================================================

BOOK_PHONE_CONFIDENCE = 0.60

EXAM_BEHAVIOR_CONFIDENCE = 0.65

PAPER_FACE_HAND_CONFIDENCE = 0.60

OBJECT_CONFIDENCE = 0.65


# ============================================================
# CPU PERFORMANCE
# ============================================================

DETECT_EVERY_N_FRAMES = 4

BOOK_PHONE_EVERY = 2

FACE_HAND_EVERY = 2

BEHAVIOR_EVERY = 4

OBJECT_EVERY = 4


# ============================================================
# EXAM CONFIGURATION
# ============================================================

exam_name = ""

exam_started = False


# ============================================================
# ALLOWED ITEMS
# ============================================================

allowed_items = []


# ============================================================
# RESTRICTED ITEMS
# ============================================================

restricted_items = [
    "phone",
    "book",
    "paper",
    "calculator",
    "earphone",
    "sunglasses",
    "watch",
]


# ============================================================
# OBJECT CATEGORIES
# ============================================================

RESTRICTED_OBJECTS = {
    "phone",
    "book",
    "paper",
    "calculator",
    "earphone",
    "sunglasses",
    "watch",
}


# ============================================================
# BEHAVIOR VIOLATIONS
# ============================================================

BEHAVIOR_VIOLATIONS = {
    "cheating",
    "cheat_paper",
    "look_around",
    "use_phone",
}


# ============================================================
# NON-VIOLATION FACE / HAND LABELS
# ============================================================

FACE_LABELS = {
    "face",
}

HAND_LABELS = {
    "fist",
    "index_left",
    "index_right",
    "open_palm",
    "point",
    "thumbs_down",
    "thumbs_up",
}


# ============================================================
# OBJECT FLAGS
# ============================================================

paper_detected = False

phone_detected = False

book_detected = False

calculator_detected = False

earphone_detected = False

sunglasses_detected = False

watch_detected = False


# ============================================================
# CURRENT DETECTION
# ============================================================

current_detected_object = ""

current_status = "RUNNING"

last_detected_object = "NONE"


# ============================================================
# DETECTED OBJECT LISTS
# ============================================================

detected_objects = []

detected_restricted_objects = []


# ============================================================
# FACE INFORMATION
# ============================================================

face_count = 0

face_status = "NO FACE"

face_verified = False

student_name = ""

student_id = ""


# ============================================================
# GAZE
# ============================================================

gaze_direction = "CENTER"


# ============================================================
# HEAD POSE
# ============================================================

head_direction = "FORWARD"


# ============================================================
# BEHAVIOR
# ============================================================

behavior_status = "NORMAL"

behavior_score = 0

behavior_reasons = []


# ============================================================
# VIOLATIONS
# ============================================================

total_violations = 0

violations = 0


# ============================================================
# VIOLATION COOLDOWN
# ============================================================

last_violation_time = 0

violation_cooldown = 5


# ============================================================
# FACE VIOLATION
# ============================================================

last_face_violation = 0

face_violation_cooldown = 5


# ============================================================
# NO FACE
# ============================================================

last_no_face_violation = 0

no_face_cooldown = 5


# ============================================================
# BEHAVIOR ALERT
# ============================================================

last_behavior_alert = 0

behavior_alert_cooldown = 5


# ============================================================
# OBJECT ALERT
# ============================================================

last_object_alert = 0

object_alert_cooldown = 5


# ============================================================
# TEMPORAL CONFIRMATION
# ============================================================

OBJECT_CONFIRM_FRAMES = 3

BEHAVIOR_CONFIRM_FRAMES = 3

DETECTION_TIMEOUT = 1.0


# ============================================================
# SCREENSHOTS
# ============================================================

SAVE_SCREENSHOTS = True

SAVE_VIOLATION_SCREENSHOTS = True


# ============================================================
# DASHBOARD
# ============================================================

dashboard = {

    "exam": "",

    "status": "NOT STARTED",

    "student_id": "",

    "student_name": "",

    # --------------------------------------------------------
    # Face
    # --------------------------------------------------------

    "face_count": 0,

    "face_status": "NO FACE",

    "face_verified": False,

    # --------------------------------------------------------
    # Gaze / head
    # --------------------------------------------------------

    "gaze": "CENTER",

    "head": "FORWARD",

    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    "object": "NONE",

    "objects": [],

    "restricted_objects": [],

    "paper": False,

    "phone": False,

    "book": False,

    "calculator": False,

    "earphone": False,

    "sunglasses": False,

    "watch": False,

    # --------------------------------------------------------
    # Behavior
    # --------------------------------------------------------

    "behavior": "NORMAL",

    "behavior_score": 0,

    "behavior_reasons": [],

    # --------------------------------------------------------
    # Violations
    # --------------------------------------------------------

    "violations": 0,
}


# ============================================================
# ESP32
# ============================================================

ESP32_ENABLED = False

ESP32_IP = "192.168.55.120"

ESP32_PORT = 80


# ============================================================
# FIREBASE
# ============================================================

FIREBASE_ENABLED = False

FIREBASE_CREDENTIALS = (
    BASE_DIR / "firebase_credentials.json"
)


# ============================================================
# DEBUG
# ============================================================

DEBUG = True


# ============================================================
# SYSTEM INFORMATION
# ============================================================

SYSTEM_NAME = (
    "AI Exam Surveillance System V2"
)

VERSION = "2.0"


# ============================================================
# CAMERA SOURCE HELPER
# ============================================================

def get_camera_source():
    """
    Return configured camera source.
    """

    if CAMERA_SOURCE.lower() == "phone":
        return PHONE_STREAM_URL

    return CAMERA_INDEX


# ============================================================
# MODEL PATHS
# ============================================================

def get_model_paths():
    """
    Return all active trained model paths.
    """

    return {

        "book_phone":
            BOOK_PHONE_MODEL,

        "exam_behavior":
            EXAM_BEHAVIOR_MODEL,

        "paper_face_hand":
            PAPER_FACE_HAND_MODEL,

        "object":
            OBJECT_MODEL,

    }


# ============================================================
# MODEL EXISTENCE CHECK
# ============================================================

def check_models():
    """
    Check whether active trained models exist.
    """

    return {

        "book_phone":
            BOOK_PHONE_MODEL.exists(),

        "exam_behavior":
            EXAM_BEHAVIOR_MODEL.exists(),

        "paper_face_hand":
            PAPER_FACE_HAND_MODEL.exists(),

        "object":
            OBJECT_MODEL.exists(),

    }


# ============================================================
# RESET DETECTION FLAGS
# ============================================================

def reset_detection_flags():

    global paper_detected
    global phone_detected
    global book_detected

    global calculator_detected
    global earphone_detected
    global sunglasses_detected
    global watch_detected

    global detected_objects
    global detected_restricted_objects

    global face_count
    global face_status


    paper_detected = False

    phone_detected = False

    book_detected = False

    calculator_detected = False

    earphone_detected = False

    sunglasses_detected = False

    watch_detected = False

    detected_objects = []

    detected_restricted_objects = []

    face_count = 0

    face_status = "NO FACE"


# ============================================================
# UPDATE OBJECT FLAG
# ============================================================

def update_object_flag(label):

    name = str(
        label
    ).strip().lower()


    global paper_detected
    global phone_detected
    global book_detected
    global calculator_detected
    global earphone_detected
    global sunglasses_detected
    global watch_detected


    if name == "paper":

        paper_detected = True

    elif name == "phone":

        phone_detected = True

    elif name == "book":

        book_detected = True

    elif name == "calculator":

        calculator_detected = True

    elif name == "earphone":

        earphone_detected = True

    elif name == "sunglasses":

        sunglasses_detected = True

    elif name == "watch":

        watch_detected = True


# ============================================================
# UPDATE FACE
# ============================================================

def update_face():

    global face_count
    global face_status

    face_count += 1

    face_status = "FACE DETECTED"


# ============================================================
# UPDATE DASHBOARD
# ============================================================

def update_dashboard():

    dashboard.update({

        "exam":
            exam_name,

        "status":
            (
                "RUNNING"
                if exam_started
                else "NOT STARTED"
            ),

        "student_id":
            student_id,

        "student_name":
            student_name,

        "face_count":
            face_count,

        "face_status":
            face_status,

        "face_verified":
            face_verified,

        "gaze":
            gaze_direction,

        "head":
            head_direction,

        "object":
            last_detected_object,

        "objects":
            list(detected_objects),

        "restricted_objects":
            list(detected_restricted_objects),

        "paper":
            paper_detected,

        "phone":
            phone_detected,

        "book":
            book_detected,

        "calculator":
            calculator_detected,

        "earphone":
            earphone_detected,

        "sunglasses":
            sunglasses_detected,

        "watch":
            watch_detected,

        "behavior":
            behavior_status,

        "behavior_score":
            behavior_score,

        "behavior_reasons":
            list(behavior_reasons),

        "violations":
            total_violations,

    })


# ============================================================
# RESET DETECTION STATE
# ============================================================

def reset_detection_state():

    global current_detected_object
    global current_status
    global last_detected_object

    global face_count
    global face_status
    global face_verified

    global gaze_direction
    global head_direction

    global behavior_status
    global behavior_score
    global behavior_reasons

    global total_violations
    global violations

    global last_violation_time
    global last_face_violation
    global last_no_face_violation
    global last_behavior_alert
    global last_object_alert


    current_detected_object = ""

    current_status = "RUNNING"

    last_detected_object = "NONE"


    reset_detection_flags()


    face_count = 0

    face_status = "NO FACE"

    face_verified = False


    gaze_direction = "CENTER"

    head_direction = "FORWARD"


    behavior_status = "NORMAL"

    behavior_score = 0

    behavior_reasons = []


    total_violations = 0

    violations = 0


    last_violation_time = 0

    last_face_violation = 0

    last_no_face_violation = 0

    last_behavior_alert = 0

    last_object_alert = 0


    update_dashboard()


# ============================================================
# RESET COMPLETE RUNTIME
# ============================================================

def reset_runtime_state():

    global exam_name
    global exam_started

    global allowed_items
    global restricted_items

    global student_name
    global student_id


    exam_name = ""

    exam_started = False

    allowed_items = []

    restricted_items = [
        "phone",
        "book",
        "paper",
        "calculator",
        "earphone",
        "sunglasses",
        "watch",
    ]

    student_name = ""

    student_id = ""


    reset_detection_state()


# ============================================================
# CONFIGURATION SUMMARY
# ============================================================

if DEBUG:

    print()
    print("=" * 70)
    print("AI EXAM SURVEILLANCE SYSTEM V2")
    print("=" * 70)

    print()
    print("CAMERA")
    print("-" * 70)

    print("Source     :", CAMERA_SOURCE)

    print(
        "Resolution :",
        CAMERA_WIDTH,
        "x",
        CAMERA_HEIGHT
    )

    if CAMERA_SOURCE.lower() == "phone":

        print("Phone IP   :", PHONE_IP)

        print("Port       :", PHONE_PORT)

        print(
            "Stream     :",
            PHONE_STREAM_URL
        )


    print()
    print("MODELS")
    print("-" * 70)

    print(
        "Book + Phone:",
        BOOK_PHONE_MODEL
    )

    print(
        "Exists:",
        BOOK_PHONE_MODEL.exists()
    )

    print(
        "Classes:",
        BOOK_PHONE_CLASSES
    )


    print()

    print(
        "Exam Behavior:",
        EXAM_BEHAVIOR_MODEL
    )

    print(
        "Exists:",
        EXAM_BEHAVIOR_MODEL.exists()
    )

    print(
        "Classes:",
        EXAM_BEHAVIOR_CLASSES
    )


    print()

    print(
        "Paper + Face + Hand:",
        PAPER_FACE_HAND_MODEL
    )

    print(
        "Exists:",
        PAPER_FACE_HAND_MODEL.exists()
    )

    print(
        "Classes:",
        PAPER_FACE_HAND_CLASSES
    )


    print()

    print(
        "Object:",
        OBJECT_MODEL
    )

    print(
        "Exists:",
        OBJECT_MODEL.exists()
    )

    print(
        "Classes:",
        OBJECT_CLASSES
    )


    print()
    print("DETECTION SETTINGS")
    print("-" * 70)

    print(
        "Book/Phone confidence :",
        BOOK_PHONE_CONFIDENCE
    )

    print(
        "Behavior confidence   :",
        EXAM_BEHAVIOR_CONFIDENCE
    )

    print(
        "Face/Hand confidence  :",
        PAPER_FACE_HAND_CONFIDENCE
    )

    print(
        "Object confidence     :",
        OBJECT_CONFIDENCE
    )

    print(
        "Object confirmation   :",
        OBJECT_CONFIRM_FRAMES
    )

    print(
        "Behavior confirmation :",
        BEHAVIOR_CONFIRM_FRAMES
    )

    print(
        "Detection timeout     :",
        DETECTION_TIMEOUT
    )


    print()
    print("RESTRICTED ITEMS")
    print("-" * 70)

    for item in restricted_items:

        print(
            "  -",
            item
        )


    print()
    print("MODEL CHECK")
    print("-" * 70)

    print(
        check_models()
    )

    print()
    print("=" * 70)
    print("CONFIG READY")
    print("=" * 70)

