
# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# SMART RULE ENGINE
# ============================================================

import config


# ============================================================
# CHECK OBJECT STATUS
# ============================================================

def check_object(label):

    if not config.exam_started:
        return "WAITING", (255, 255, 255)

    label = str(
        label if label is not None else ""
    ).strip().lower()

    allowed_items = getattr(
        config,
        "allowed_items",
        []
    ) or []

    restricted_items = getattr(
        config,
        "restricted_items",
        []
    ) or []

    allowed_items = [
        str(item).strip().lower()
        for item in allowed_items
    ]

    restricted_items = [
        str(item).strip().lower()
        for item in restricted_items
    ]

    selected_items = (
        allowed_items
        + restricted_items
    )

    # --------------------------------------------------------
    # Ignore objects not selected for this exam
    # --------------------------------------------------------

    if label not in selected_items:
        return "IGNORE", (150, 150, 150)

    # --------------------------------------------------------
    # Restricted item
    # --------------------------------------------------------

    if label in restricted_items:

        config.current_detected_object = label
        config.current_status = "VIOLATION"

        return "VIOLATION", (0, 0, 255)

    # --------------------------------------------------------
    # Allowed item
    # --------------------------------------------------------

    if label in allowed_items:

        config.current_detected_object = label
        config.current_status = "ALLOWED"

        return "ALLOWED", (0, 255, 0)

    return "UNKNOWN", (255, 255, 255)


# ============================================================
# FACE RULES
# ============================================================

def check_face():

    face_count = getattr(
        config,
        "face_count",
        0
    )

    try:
        face_count = int(face_count)
    except Exception:
        face_count = 0

    if face_count == 0:
        return "NO FACE"

    if face_count == 1:
        return "NORMAL"

    return "MULTIPLE FACES"


# ============================================================
# HEAD POSE RULES
# ============================================================

def check_head():

    direction = str(
        getattr(
            config,
            "head_direction",
            "FORWARD"
        )
    ).strip().upper()

    if direction == "FORWARD":
        return False

    return True


# ============================================================
# EYE GAZE RULES
# ============================================================

def check_gaze():

    direction = str(
        getattr(
            config,
            "gaze_direction",
            "CENTER"
        )
    ).strip().upper()

    if direction == "CENTER":
        return False

    return True


# ============================================================
# OVERALL STUDENT STATUS
# ============================================================

def get_student_status():

    face_count = getattr(
        config,
        "face_count",
        0
    )

    try:
        face_count = int(face_count)
    except Exception:
        face_count = 0

    # --------------------------------------------------------
    # Face status has highest priority
    # --------------------------------------------------------

    if face_count == 0:
        return "NO FACE"

    if face_count > 1:
        return "MULTIPLE FACES"

    # --------------------------------------------------------
    # Restricted object
    # --------------------------------------------------------

    if getattr(
        config,
        "current_status",
        ""
    ) == "VIOLATION":

        return "OBJECT VIOLATION"

    # --------------------------------------------------------
    # Head movement
    # --------------------------------------------------------

    if check_head():

        return "HEAD TURN"

    # --------------------------------------------------------
    # Eye gaze
    # --------------------------------------------------------

    if check_gaze():

        return "LOOKING AWAY"

    # --------------------------------------------------------
    # Normal
    # --------------------------------------------------------

    return "NORMAL"


# ============================================================
# GET CURRENT VIOLATION
# ============================================================

def get_current_violation():

    status = getattr(
        config,
        "current_status",
        ""
    )

    if status != "VIOLATION":

        return None

    label = getattr(
        config,
        "current_detected_object",
        ""
    )

    if not label:

        return None

    return str(label)


# ============================================================
# RESET OBJECT STATUS
# ============================================================

def reset_object_status():

    try:

        config.current_detected_object = ""

    except Exception:
        pass

    try:

        config.current_status = "NORMAL"

    except Exception:
        pass


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("SMART RULE ENGINE TEST")
    print("=" * 60)

    print()

    print("Exam started:",
          getattr(config, "exam_started", False))

    print("Allowed items:",
          getattr(config, "allowed_items", []))

    print("Restricted items:",
          getattr(config, "restricted_items", []))

    print()

    # --------------------------------------------------------
    # Face tests
    # --------------------------------------------------------

    original_face_count = getattr(
        config,
        "face_count",
        0
    )

    original_exam_started = getattr(
        config,
        "exam_started",
        False
    )

    print("Face rule tests:")

    config.face_count = 0
    print("0 faces ->", check_face())

    config.face_count = 1
    print("1 face  ->", check_face())

    config.face_count = 2
    print("2 faces ->", check_face())

    # --------------------------------------------------------
    # Head / gaze tests
    # --------------------------------------------------------

    original_head = getattr(
        config,
        "head_direction",
        "FORWARD"
    )

    original_gaze = getattr(
        config,
        "gaze_direction",
        "CENTER"
    )

    config.head_direction = "FORWARD"
    print()
    print("Forward head -> violation:",
          check_head())

    config.head_direction = "LEFT"
    print("Left head -> violation:",
          check_head())

    config.gaze_direction = "CENTER"
    print("Center gaze -> violation:",
          check_gaze())

    config.gaze_direction = "LEFT"
    print("Left gaze -> violation:",
          check_gaze())

    # --------------------------------------------------------
    # Restore values
    # --------------------------------------------------------

    config.face_count = original_face_count
    config.exam_started = original_exam_started
    config.head_direction = original_head
    config.gaze_direction = original_gaze

    print()
    print("Current student status:",
          get_student_status())

    print()
    print("=" * 60)
    print("RULE ENGINE TEST COMPLETE")
    print("=" * 60)
