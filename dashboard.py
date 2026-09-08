
# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# DASHBOARD DATA MODULE
# ============================================================

import config


# ============================================================
# SAFE CONFIG VALUE
# ============================================================

def _get(name, default=None):
    """
    Safely read a value from config.py.
    """
    try:
        return getattr(config, name, default)
    except Exception:
        return default


# ============================================================
# SAFE LIST
# ============================================================

def _get_list(name):
    """
    Return a safe list copy from config.py.
    """
    value = _get(name, [])

    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        return list(value)

    return [value]


# ============================================================
# SAFE INTEGER
# ============================================================

def _get_int(name, default=0):
    """
    Safely convert config value to integer.
    """
    try:
        return int(_get(name, default))
    except (TypeError, ValueError):
        return default


# ============================================================
# SAFE FLOAT
# ============================================================

def _get_float(name, default=0.0):
    """
    Safely convert config value to float.
    """
    try:
        return float(_get(name, default))
    except (TypeError, ValueError):
        return default


# ============================================================
# SAFE BOOLEAN
# ============================================================

def _get_bool(name, default=False):
    """
    Safely convert config value to boolean.
    """
    value = _get(name, default)

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in (
            "true",
            "1",
            "yes",
            "y",
            "on",
            "running",
            "connected",
        )

    return bool(value)


# ============================================================
# SAFE STRING
# ============================================================

def _get_str(name, default=""):
    """
    Safely convert config value to string.
    """
    value = _get(name, default)

    if value is None:
        return str(default)

    return str(value)


# ============================================================
# CAMERA STATUS
# ============================================================

def _camera_connected():
    """
    Safely check camera connection.

    Dashboard must never crash if camera.py is unavailable
    or the camera object is not initialized.
    """

    try:
        from camera import camera

        if camera is None:
            return False

        # ----------------------------------------------------
        # Preferred camera API
        # ----------------------------------------------------

        is_connected = getattr(
            camera,
            "is_connected",
            None
        )

        if callable(is_connected):
            try:
                return bool(is_connected())
            except Exception:
                pass

        # ----------------------------------------------------
        # Fallback: check OpenCV capture object
        # ----------------------------------------------------

        cap = getattr(
            camera,
            "cap",
            None
        )

        if cap is not None:

            is_opened = getattr(
                cap,
                "isOpened",
                None
            )

            if callable(is_opened):
                try:
                    return bool(is_opened())
                except Exception:
                    pass

        # ----------------------------------------------------
        # Other possible camera attributes
        # ----------------------------------------------------

        for attr in (
            "connected",
            "camera_connected",
            "running",
        ):

            value = getattr(
                camera,
                attr,
                None
            )

            if value is not None:
                return bool(value)

        return False

    except Exception:
        return False


# ============================================================
# CAMERA URL
# ============================================================

def _camera_url():
    """
    Return the currently configured camera URL if available.
    """

    for name in (
        "camera_url",
        "CAMERA_URL",
        "phone_stream_url",
        "PHONE_STREAM_URL",
        "stream_url",
        "STREAM_URL",
    ):

        value = _get(name, None)

        if value:
            return str(value)

    return ""


# ============================================================
# EXAM STATUS
# ============================================================

def _exam_status(exam_started):
    """
    Convert exam_started state into dashboard status.
    """

    if exam_started:
        return "RUNNING", "RUNNING"

    return "STOPPED", "NOT STARTED"


# ============================================================
# DASHBOARD CACHE UPDATE
# ============================================================

def _update_dashboard_cache(data):
    """
    Keep config.dashboard synchronized if config.py
    contains a dashboard dictionary.
    """

    try:

        dashboard = getattr(
            config,
            "dashboard",
            None
        )

        if not isinstance(dashboard, dict):
            return

        dashboard.update({

            # ------------------------------------------------
            # Exam
            # ------------------------------------------------

            "exam":
                data["exam_name"],

            "exam_name":
                data["exam_name"],

            "exam_status":
                data["exam_status"],

            "status":
                data["status"],

            "exam_started":
                data["exam_started"],

            # ------------------------------------------------
            # Student
            # ------------------------------------------------

            "student_id":
                data["student_id"],

            "student_name":
                data["student_name"],

            # ------------------------------------------------
            # Face
            # ------------------------------------------------

            "face_count":
                data["face_count"],

            "face_status":
                data["face_status"],

            "face_verified":
                data["face_verified"],

            # ------------------------------------------------
            # Head / Gaze
            # ------------------------------------------------

            "head":
                data["head_direction"],

            "head_direction":
                data["head_direction"],

            "gaze":
                data["gaze_direction"],

            "gaze_direction":
                data["gaze_direction"],

            # ------------------------------------------------
            # Objects
            # ------------------------------------------------

            "object":
                data["detected_object"],

            "detected_object":
                data["detected_object"],

            "last_detected_object":
                data["last_detected_object"],

            "current_detected_object":
                data["current_detected_object"],

            "current_status":
                data["current_status"],

            # ------------------------------------------------
            # Paper
            # ------------------------------------------------

            "paper":
                data["paper_detected"],

            "paper_detected":
                data["paper_detected"],

            # ------------------------------------------------
            # Phone
            # ------------------------------------------------

            "phone":
                data["phone_detected"],

            "phone_detected":
                data["phone_detected"],

            # ------------------------------------------------
            # Book
            # ------------------------------------------------

            "book":
                data["book_detected"],

            "book_detected":
                data["book_detected"],

            # ------------------------------------------------
            # Behavior
            # ------------------------------------------------

            "behavior":
                data["behavior_status"],

            "behavior_status":
                data["behavior_status"],

            "behavior_score":
                data["behavior_score"],

            "behavior_reasons":
                list(data["behavior_reasons"]),

            # ------------------------------------------------
            # Violations
            # ------------------------------------------------

            "violations":
                data["total_violations"],

            "total_violations":
                data["total_violations"],

            # ------------------------------------------------
            # Camera
            # ------------------------------------------------

            "camera_connected":
                data["camera_connected"],

            "camera_url":
                data["camera_url"],

        })

    except Exception:
        # Cache update should NEVER break dashboard API.
        pass


# ============================================================
# GET DASHBOARD DATA
# ============================================================

def get_dashboard_data():
    """
    Return the complete current surveillance state.

    IMPORTANT:
    This function ONLY reads runtime/configuration state.

    It does NOT:
        - start camera
        - stop camera
        - run YOLO
        - create violations
        - save screenshots
        - modify detector counters
    """

    try:

        # ====================================================
        # EXAM
        # ====================================================

        exam_name = _get_str(
            "exam_name",
            ""
        )

        exam_started = _get_bool(
            "exam_started",
            False
        )

        exam_status, status = _exam_status(
            exam_started
        )


        # ====================================================
        # STUDENT
        # ====================================================

        student_name = _get_str(
            "student_name",
            ""
        )

        student_id = _get_str(
            "student_id",
            ""
        )


        # ====================================================
        # FACE
        # ====================================================

        face_count = _get_int(
            "face_count",
            0
        )

        if face_count < 0:
            face_count = 0

        face_status = _get_str(
            "face_status",
            "NO FACE"
        )

        if not face_status:
            face_status = "NO FACE"

        face_verified = _get_bool(
            "face_verified",
            False
        )


        # ====================================================
        # HEAD
        # ====================================================

        head_direction = _get_str(
            "head_direction",
            "FORWARD"
        )

        if not head_direction:
            head_direction = "FORWARD"


        # ====================================================
        # GAZE
        # ====================================================

        gaze_direction = _get_str(
            "gaze_direction",
            "CENTER"
        )

        if not gaze_direction:
            gaze_direction = "CENTER"


        # ====================================================
        # OBJECT DETECTION
        # ====================================================

        current_detected_object = _get_str(
            "current_detected_object",
            ""
        )

        last_detected_object = _get_str(
            "last_detected_object",
            "NONE"
        )

        if not last_detected_object:
            last_detected_object = "NONE"

        current_status = _get_str(
            "current_status",
            ""
        )


        # ====================================================
        # OBJECT FLAGS
        # ====================================================

        paper_detected = _get_bool(
            "paper_detected",
            False
        )

        phone_detected = _get_bool(
            "phone_detected",
            False
        )

        book_detected = _get_bool(
            "book_detected",
            False
        )


        # ====================================================
        # BEHAVIOR
        # ====================================================

        behavior_status = _get_str(
            "behavior_status",
            "NORMAL"
        )

        if not behavior_status:
            behavior_status = "NORMAL"

        behavior_score = _get_int(
            "behavior_score",
            0
        )

        if behavior_score < 0:
            behavior_score = 0

        behavior_reasons = _get_list(
            "behavior_reasons"
        )


        # ====================================================
        # VIOLATIONS
        # ====================================================

        total_violations = _get_int(
            "total_violations",
            0
        )

        if total_violations < 0:
            total_violations = 0

        # Compatibility with code that may only use
        # "violations".
        if total_violations == 0:

            alternate_violations = _get_int(
                "violations",
                0
            )

            if alternate_violations > 0:
                total_violations = alternate_violations


        # ====================================================
        # ALLOWED ITEMS
        # ====================================================

        allowed_items = _get_list(
            "allowed_items"
        )


        # ====================================================
        # RESTRICTED ITEMS
        # ====================================================

        restricted_items = _get_list(
            "restricted_items"
        )


        # ====================================================
        # CAMERA
        # ====================================================

        camera_connected = _camera_connected()

        camera_url = _camera_url()


        # ====================================================
        # YOLO / SYSTEM INFO
        # ====================================================

        confidence = _get_float(
            "confidence",
            _get_float(
                "YOLO_CONFIDENCE",
                0.3
            )
        )

        inference_size = _get_int(
            "inference_size",
            _get_int(
                "YOLO_INFERENCE_SIZE",
                320
            )
        )

        detection_interval = _get_int(
            "detection_interval",
            _get_int(
                "DETECTION_INTERVAL",
                4
            )
        )


        # ====================================================
        # DASHBOARD DATA
        # ====================================================

        data = {

            # ------------------------------------------------
            # Exam
            # ------------------------------------------------

            "exam_name":
                exam_name,

            "exam":
                exam_name,

            "exam_status":
                exam_status,

            "status":
                status,

            "exam_started":
                exam_started,


            # ------------------------------------------------
            # Student
            # ------------------------------------------------

            "student_name":
                student_name,

            "student_id":
                student_id,


            # ------------------------------------------------
            # Allowed / Restricted
            # ------------------------------------------------

            "allowed_items":
                allowed_items,

            "restricted_items":
                restricted_items,


            # ------------------------------------------------
            # Face
            # ------------------------------------------------

            "face_count":
                face_count,

            "face_status":
                face_status,

            "face_verified":
                face_verified,


            # ------------------------------------------------
            # Head / Gaze
            # ------------------------------------------------

            "head_direction":
                head_direction,

            "head":
                head_direction,

            "gaze_direction":
                gaze_direction,

            "gaze":
                gaze_direction,


            # ------------------------------------------------
            # Objects
            # ------------------------------------------------

            "detected_object":
                last_detected_object,

            "last_detected_object":
                last_detected_object,

            "current_detected_object":
                current_detected_object,

            "current_status":
                current_status,


            # ------------------------------------------------
            # Paper
            # ------------------------------------------------

            "paper":
                paper_detected,

            "paper_detected":
                paper_detected,


            # ------------------------------------------------
            # Phone
            # ------------------------------------------------

            "phone":
                phone_detected,

            "phone_detected":
                phone_detected,


            # ------------------------------------------------
            # Book
            # ------------------------------------------------

            "book":
                book_detected,

            "book_detected":
                book_detected,


            # ------------------------------------------------
            # Behavior
            # ------------------------------------------------

            "behavior":
                behavior_status,

            "behavior_status":
                behavior_status,

            "behavior_score":
                behavior_score,

            "behavior_reasons":
                behavior_reasons,


            # ------------------------------------------------
            # Violations
            # ------------------------------------------------

            "violations":
                total_violations,

            "total_violations":
                total_violations,


            # ------------------------------------------------
            # Camera
            # ------------------------------------------------

            "camera_connected":
                camera_connected,

            "camera_url":
                camera_url,


            # ------------------------------------------------
            # Optional System Information
            # ------------------------------------------------

            "confidence":
                confidence,

            "inference_size":
                inference_size,

            "detection_interval":
                detection_interval,

        }


        # ====================================================
        # UPDATE CACHE
        # ====================================================

        _update_dashboard_cache(
            data
        )


        # ====================================================
        # RETURN
        # ====================================================

        return data


    # ========================================================
    # SAFE FALLBACK
    # ========================================================

    except Exception as e:

        print(
            "Dashboard data error:",
            e
        )

        # ----------------------------------------------------
        # Recover basic exam state
        # ----------------------------------------------------

        exam_name = _get_str(
            "exam_name",
            ""
        )

        exam_started = _get_bool(
            "exam_started",
            False
        )

        fallback_exam_status, fallback_status = (
            _exam_status(
                exam_started
            )
        )

        # ----------------------------------------------------
        # Return complete fallback structure
        # ----------------------------------------------------

        return {

            "exam_name":
                exam_name,

            "exam":
                exam_name,

            "exam_status":
                fallback_exam_status,

            "status":
                fallback_status,

            "exam_started":
                exam_started,


            "student_name":
                _get_str(
                    "student_name",
                    ""
                ),

            "student_id":
                _get_str(
                    "student_id",
                    ""
                ),


            "allowed_items":
                _get_list(
                    "allowed_items"
                ),

            "restricted_items":
                _get_list(
                    "restricted_items"
                ),


            "face_count":
                0,

            "face_status":
                "NO FACE",

            "face_verified":
                False,


            "head_direction":
                "FORWARD",

            "head":
                "FORWARD",


            "gaze_direction":
                "CENTER",

            "gaze":
                "CENTER",


            "detected_object":
                "NONE",

            "last_detected_object":
                "NONE",

            "current_detected_object":
                "",

            "current_status":
                "",


            "paper":
                False,

            "paper_detected":
                False,


            "phone":
                False,

            "phone_detected":
                False,


            "book":
                False,

            "book_detected":
                False,


            "behavior":
                "NORMAL",

            "behavior_status":
                "NORMAL",

            "behavior_score":
                0,

            "behavior_reasons":
                [],


            "violations":
                0,

            "total_violations":
                0,


            "camera_connected":
                False,

            "camera_url":
                _camera_url(),


            "confidence":
                0.3,

            "inference_size":
                320,

            "detection_interval":
                4,

        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()

    print("=" * 60)
    print("DASHBOARD DATA TEST")
    print("=" * 60)

    try:

        data = get_dashboard_data()

        for key, value in data.items():

            print(
                f"{key}: {value}"
            )

        print("=" * 60)
        print("DASHBOARD TEST OK")
        print("=" * 60)

    except Exception as e:

        print("=" * 60)
        print("DASHBOARD TEST FAILED")
        print("Error:", e)
        print("=" * 60)

