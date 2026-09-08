
# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# FLASK APPLICATION
#
# Responsibilities:
# ------------------------------------------------------------
# 1. Web dashboard
# 2. Live camera stream
# 3. Start / Stop exam
# 4. Dashboard API
# 5. Camera status API
# 6. System status API
# 7. Violation reset
# 8. Safe application shutdown
# ============================================================

from flask import (
    Flask,
    render_template,
    Response,
    request,
    redirect,
    url_for,
    jsonify,
)

import atexit
import threading

import config

from camera import camera, generate_frames
from dashboard import get_dashboard_data


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# GLOBAL STATE LOCK
# ============================================================

_state_lock = threading.RLock()


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_camera_connected():
    """
    Safely check camera connection.
    """

    try:

        if camera is None:
            return False

        method = getattr(
            camera,
            "is_connected",
            None
        )

        if not callable(method):
            return False

        return bool(
            method()
        )

    except Exception:
        return False


def safe_camera_running():
    """
    Safely read camera running state.
    """

    try:

        if camera is None:
            return False

        return bool(
            getattr(
                camera,
                "running",
                False
            )
        )

    except Exception:
        return False


def safe_camera_frames():
    """
    Safely read camera frame counter.
    """

    try:

        if camera is None:
            return 0

        value = int(
            getattr(
                camera,
                "frame_count",
                0
            )
        )

        return max(
            0,
            value
        )

    except (TypeError, ValueError):
        return 0


def safe_camera_source():
    """
    Safely return camera source.
    """

    try:

        if camera is not None:

            source = getattr(
                camera,
                "source",
                None
            )

            if source is not None:
                return source

    except Exception:
        pass

    try:

        return config.get_camera_source()

    except Exception:

        return getattr(
            config,
            "CAMERA_SOURCE",
            "unknown"
        )


def safe_list(value):
    """
    Safely convert a value to a list.
    """

    if value is None:
        return []

    if isinstance(
        value,
        (list, tuple, set)
    ):
        return list(value)

    return [value]


def safe_int(value, default=0):
    """
    Safely convert value to integer.
    """

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_bool(value, default=False):
    """
    Safely convert value to boolean.
    """

    if isinstance(value, bool):
        return value

    if isinstance(value, str):

        return value.strip().lower() in (
            "true",
            "1",
            "yes",
            "on",
            "running",
        )

    if value is None:
        return default

    return bool(value)


# ============================================================
# RESET DETECTION STATE
# ============================================================

def reset_detection_state():
    """
    Reset current detection/dashboard state.

    This function does NOT change exam_started,
    exam_name, student information, or exam configuration.
    """

    with _state_lock:

        # ----------------------------------------------------
        # Objects
        # ----------------------------------------------------

        config.paper_detected = False
        config.phone_detected = False
        config.book_detected = False

        config.current_detected_object = ""
        config.last_detected_object = "NONE"
        config.current_status = ""


        # ----------------------------------------------------
        # Face
        # ----------------------------------------------------

        config.face_count = 0
        config.face_status = "NO FACE"
        config.face_verified = False


        # ----------------------------------------------------
        # Gaze
        # ----------------------------------------------------

        config.gaze_direction = "CENTER"


        # ----------------------------------------------------
        # Head
        # ----------------------------------------------------

        config.head_direction = "FORWARD"


        # ----------------------------------------------------
        # Behavior
        # ----------------------------------------------------

        config.behavior_status = "NORMAL"
        config.behavior_score = 0
        config.behavior_reasons = []


        # ----------------------------------------------------
        # Violations
        # ----------------------------------------------------

        config.total_violations = 0
        config.last_violation_time = 0


# ============================================================
# RESET EXAM STATE
# ============================================================

def reset_exam_state():
    """
    Reset detection and detector temporal state.

    Does NOT modify:
        exam_started
        exam_name
        student_name
        student_id
        allowed_items
        restricted_items
    """

    with _state_lock:

        reset_detection_state()


        # ----------------------------------------------------
        # Reset timers
        # ----------------------------------------------------

        config.last_face_violation = 0
        config.last_no_face_violation = 0
        config.last_behavior_alert = 0
        config.last_object_alert = 0


        # ----------------------------------------------------
        # Reset detector internal state
        # ----------------------------------------------------

        try:

            from detector import reset_detector_state

            reset_detector_state()

        except Exception as e:

            print(
                "Detector reset warning:",
                e
            )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    """
    Main dashboard page.
    """

    return render_template(
        "index.html"
    )


# ============================================================
# LIVE CAMERA
# ============================================================

@app.route("/video")
def video():
    """
    MJPEG live camera stream.
    """

    try:

        if camera is None:

            return Response(
                "Camera unavailable.",
                status=503,
                mimetype="text/plain"
            )

        return Response(

            generate_frames(),

            mimetype=(
                "multipart/x-mixed-replace;"
                " boundary=frame"
            ),

            headers={

                "Cache-Control": (
                    "no-cache, "
                    "no-store, "
                    "must-revalidate"
                ),

                "Pragma": "no-cache",

                "Expires": "0",

                "Connection": "close",

            },
        )

    except Exception as e:

        print(
            "Video stream error:",
            e
        )

        return Response(
            "Camera stream unavailable.",
            status=503,
            mimetype="text/plain"
        )


# ============================================================
# DASHBOARD API
# ============================================================

@app.route("/dashboard_data")
def dashboard_data():
    """
    Return current dashboard state as JSON.
    """

    try:

        # Read the complete state while protected
        # against simultaneous exam state changes.

        with _state_lock:

            data = get_dashboard_data()

            if not isinstance(
                data,
                dict
            ):

                data = build_dashboard_fallback()

            # Camera state is always refreshed here.

            data["camera_connected"] = (
                safe_camera_connected()
            )

            return jsonify(data)

    except Exception as e:

        print(
            "Dashboard API error:",
            e
        )

        return jsonify(
            build_dashboard_fallback(
                error=str(e)
            )
        )


# ============================================================
# DASHBOARD FALLBACK
# ============================================================

def build_dashboard_fallback(error=None):
    """
    Build a safe dashboard response if dashboard.py
    fails for any reason.
    """

    try:

        exam_started = safe_bool(
            getattr(
                config,
                "exam_started",
                False
            )
        )

        exam_name = str(
            getattr(
                config,
                "exam_name",
                ""
            ) or ""
        )

        face_count = safe_int(
            getattr(
                config,
                "face_count",
                0
            ),
            0
        )

        face_count = max(
            0,
            face_count
        )

        behavior_score = safe_int(
            getattr(
                config,
                "behavior_score",
                0
            ),
            0
        )

        behavior_score = max(
            0,
            behavior_score
        )

        violations = safe_int(
            getattr(
                config,
                "total_violations",
                0
            ),
            0
        )

        violations = max(
            0,
            violations
        )

        behavior_reasons = safe_list(
            getattr(
                config,
                "behavior_reasons",
                []
            )
        )

        data = {

            "exam_name": exam_name,

            "exam": exam_name,

            "exam_status": (
                "RUNNING"
                if exam_started
                else "STOPPED"
            ),

            "status": (
                "RUNNING"
                if exam_started
                else "NOT STARTED"
            ),

            "exam_started": exam_started,

            "student_id": str(
                getattr(
                    config,
                    "student_id",
                    ""
                ) or ""
            ),

            "student_name": str(
                getattr(
                    config,
                    "student_name",
                    ""
                ) or ""
            ),

            "allowed_items": safe_list(
                getattr(
                    config,
                    "allowed_items",
                    []
                )
            ),

            "restricted_items": safe_list(
                getattr(
                    config,
                    "restricted_items",
                    []
                )
            ),

            "face_count": face_count,

            "face_status": str(
                getattr(
                    config,
                    "face_status",
                    "NO FACE"
                ) or "NO FACE"
            ),

            "face_verified": safe_bool(
                getattr(
                    config,
                    "face_verified",
                    False
                )
            ),

            "gaze_direction": str(
                getattr(
                    config,
                    "gaze_direction",
                    "CENTER"
                ) or "CENTER"
            ),

            "gaze": str(
                getattr(
                    config,
                    "gaze_direction",
                    "CENTER"
                ) or "CENTER"
            ),

            "head_direction": str(
                getattr(
                    config,
                    "head_direction",
                    "FORWARD"
                ) or "FORWARD"
            ),

            "head": str(
                getattr(
                    config,
                    "head_direction",
                    "FORWARD"
                ) or "FORWARD"
            ),

            "detected_object": str(
                getattr(
                    config,
                    "last_detected_object",
                    "NONE"
                ) or "NONE"
            ),

            "last_detected_object": str(
                getattr(
                    config,
                    "last_detected_object",
                    "NONE"
                ) or "NONE"
            ),

            "current_detected_object": str(
                getattr(
                    config,
                    "current_detected_object",
                    ""
                ) or ""
            ),

            "current_status": str(
                getattr(
                    config,
                    "current_status",
                    ""
                ) or ""
            ),

            "paper": safe_bool(
                getattr(
                    config,
                    "paper_detected",
                    False
                )
            ),

            "paper_detected": safe_bool(
                getattr(
                    config,
                    "paper_detected",
                    False
                )
            ),

            "phone": safe_bool(
                getattr(
                    config,
                    "phone_detected",
                    False
                )
            ),

            "phone_detected": safe_bool(
                getattr(
                    config,
                    "phone_detected",
                    False
                )
            ),

            "book": safe_bool(
                getattr(
                    config,
                    "book_detected",
                    False
                )
            ),

            "book_detected": safe_bool(
                getattr(
                    config,
                    "book_detected",
                    False
                )
            ),

            "behavior": str(
                getattr(
                    config,
                    "behavior_status",
                    "NORMAL"
                ) or "NORMAL"
            ),

            "behavior_status": str(
                getattr(
                    config,
                    "behavior_status",
                    "NORMAL"
                ) or "NORMAL"
            ),

            "behavior_score": behavior_score,

            "behavior_reasons": (
                behavior_reasons
            ),

            "violations": violations,

            "total_violations": violations,

            "camera_connected": (
                safe_camera_connected()
            ),
        }

        if error:
            data["api_error"] = str(error)

        return data

    except Exception as fallback_error:

        print(
            "Dashboard fallback error:",
            fallback_error
        )

        return {

            "exam_name": "",
            "exam": "",

            "exam_status": "STOPPED",
            "status": "NOT STARTED",
            "exam_started": False,

            "student_id": "",
            "student_name": "",

            "allowed_items": [],
            "restricted_items": [],

            "face_count": 0,
            "face_status": "NO FACE",
            "face_verified": False,

            "gaze_direction": "CENTER",
            "gaze": "CENTER",

            "head_direction": "FORWARD",
            "head": "FORWARD",

            "detected_object": "NONE",
            "last_detected_object": "NONE",
            "current_detected_object": "",
            "current_status": "",

            "paper": False,
            "paper_detected": False,

            "phone": False,
            "phone_detected": False,

            "book": False,
            "book_detected": False,

            "behavior": "NORMAL",
            "behavior_status": "NORMAL",
            "behavior_score": 0,
            "behavior_reasons": [],

            "violations": 0,
            "total_violations": 0,

            "camera_connected": False,

            "api_error": str(
                error or fallback_error
            ),
        }


# ============================================================
# START EXAM
# ============================================================

@app.route(
    "/start_exam",
    methods=["POST"]
)
def start_exam():
    """
    Start a new exam session.
    """

    with _state_lock:

        # ----------------------------------------------------
        # Exam name
        # ----------------------------------------------------

        exam_name = request.form.get(
            "exam_name",
            ""
        ).strip()


        # ----------------------------------------------------
        # Allowed items
        # ----------------------------------------------------

        allowed = request.form.getlist(
            "allowed"
        )


        # ----------------------------------------------------
        # Restricted items
        # ----------------------------------------------------

        restricted = request.form.getlist(
            "restricted"
        )


        # ----------------------------------------------------
        # Clean allowed list
        # ----------------------------------------------------

        allowed = list(
            dict.fromkeys(

                item.strip().lower()

                for item in allowed

                if item
                and item.strip()

            )
        )


        # ----------------------------------------------------
        # Clean restricted list
        # ----------------------------------------------------

        restricted = list(
            dict.fromkeys(

                item.strip().lower()

                for item in restricted

                if item
                and item.strip()

            )
        )


        # ----------------------------------------------------
        # Default restricted items
        # ----------------------------------------------------

        if not restricted:

            restricted = [
                "phone",
                "book",
                "paper",
            ]


        # ----------------------------------------------------
        # Restricted has priority
        # ----------------------------------------------------

        allowed = [
            item
            for item in allowed
            if item not in restricted
        ]


        # ----------------------------------------------------
        # Save exam configuration
        # ----------------------------------------------------

        config.exam_name = exam_name

        config.allowed_items = allowed

        config.restricted_items = restricted


        # ----------------------------------------------------
        # Mark exam active
        # ----------------------------------------------------

        config.exam_started = True


        # ----------------------------------------------------
        # Reset previous detection state
        # ----------------------------------------------------

        reset_exam_state()


        # ----------------------------------------------------
        # Console
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("EXAM STARTED")
        print("=" * 70)

        print(
            "Exam      :",
            config.exam_name
        )

        print(
            "Allowed   :",
            config.allowed_items
        )

        print(
            "Restricted:",
            config.restricted_items
        )

        print("=" * 70)
        print()


    return redirect(
        url_for("home")
    )


# ============================================================
# STOP EXAM
# ============================================================

@app.route(
    "/stop_exam",
    methods=["POST"]
)
def stop_exam():
    """
    Stop current exam and clear all exam state.
    """

    with _state_lock:

        # ----------------------------------------------------
        # Stop exam
        # ----------------------------------------------------

        config.exam_started = False


        # ----------------------------------------------------
        # Reset detection
        # ----------------------------------------------------

        reset_detection_state()


        # ----------------------------------------------------
        # Reset timers
        # ----------------------------------------------------

        config.last_face_violation = 0
        config.last_no_face_violation = 0
        config.last_behavior_alert = 0
        config.last_object_alert = 0


        # ----------------------------------------------------
        # Reset detector state
        # ----------------------------------------------------

        try:

            from detector import reset_detector_state

            reset_detector_state()

        except Exception as e:

            print(
                "Detector reset warning:",
                e
            )


        # ----------------------------------------------------
        # Clear exam configuration
        # ----------------------------------------------------

        config.allowed_items = []
        config.restricted_items = []
        config.exam_name = ""


        # ----------------------------------------------------
        # Clear student information
        # ----------------------------------------------------

        config.student_name = ""
        config.student_id = ""


        # ----------------------------------------------------
        # Console
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("EXAM STOPPED")
        print("=" * 70)
        print()


    return redirect(
        url_for("home")
    )


# ============================================================
# RESET VIOLATIONS
# ============================================================

@app.route(
    "/reset",
    methods=["POST"]
)
def reset():
    """
    Reset violation counter without stopping the exam.
    """

    with _state_lock:

        config.total_violations = 0
        config.last_violation_time = 0

        config.last_detected_object = "NONE"
        config.current_detected_object = ""
        config.current_status = ""


        # ----------------------------------------------------
        # Reset alert timers
        # ----------------------------------------------------

        config.last_face_violation = 0
        config.last_no_face_violation = 0
        config.last_behavior_alert = 0
        config.last_object_alert = 0


        print(
            "Violations reset."
        )


    return jsonify({

        "status": "success",

        "violations": 0,

    })


# ============================================================
# CAMERA STATUS
# ============================================================

@app.route("/camera_status")
def camera_status():
    """
    Return camera connection and runtime information.
    """

    try:

        return jsonify({

            "connected": (
                safe_camera_connected()
            ),

            "running": (
                safe_camera_running()
            ),

            "frames": (
                safe_camera_frames()
            ),

            "source": (
                safe_camera_source()
            ),

        })

    except Exception as e:

        print(
            "Camera status error:",
            e
        )

        return jsonify({

            "connected": False,

            "running": False,

            "frames": 0,

            "source": safe_camera_source(),

            "error": str(e),

        })


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.route("/status")
def status():
    """
    Return overall application status.
    """

    with _state_lock:

        return jsonify({

            "system": getattr(
                config,
                "SYSTEM_NAME",
                "AI Exam Surveillance System V2"
            ),

            "version": getattr(
                config,
                "VERSION",
                "2.0"
            ),

            "exam_started": safe_bool(
                getattr(
                    config,
                    "exam_started",
                    False
                )
            ),

            "exam_name": str(
                getattr(
                    config,
                    "exam_name",
                    ""
                ) or ""
            ),

            "camera_connected": (
                safe_camera_connected()
            ),

            "violations": max(
                0,
                safe_int(
                    getattr(
                        config,
                        "total_violations",
                        0
                    ),
                    0
                )
            ),

        })


# ============================================================
# EXAM CONFIG API
# ============================================================

@app.route("/exam_config")
def exam_config():
    """
    Return currently active exam configuration.
    """

    with _state_lock:

        return jsonify({

            "exam_started": safe_bool(
                getattr(
                    config,
                    "exam_started",
                    False
                )
            ),

            "exam_name": str(
                getattr(
                    config,
                    "exam_name",
                    ""
                ) or ""
            ),

            "allowed_items": safe_list(
                getattr(
                    config,
                    "allowed_items",
                    []
                )
            ),

            "restricted_items": safe_list(
                getattr(
                    config,
                    "restricted_items",
                    []
                )
            ),

        })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():
    """
    Simple health endpoint.
    """

    return jsonify({

        "status": "OK",

        "system": getattr(
            config,
            "SYSTEM_NAME",
            "AI Exam Surveillance System V2"
        ),

        "version": getattr(
            config,
            "VERSION",
            "2.0"
        ),

        "camera_connected": (
            safe_camera_connected()
        ),

    })


# ============================================================
# APPLICATION SHUTDOWN
# ============================================================

def shutdown_camera():
    """
    Safely release camera.
    """

    try:

        if camera is not None:

            release_method = getattr(
                camera,
                "release",
                None
            )

            if callable(release_method):

                release_method()

                print(
                    "Camera released."
                )

    except Exception as e:

        print(
            "Camera shutdown error:",
            e
        )


# ============================================================
# REGISTER SHUTDOWN HANDLER
# ============================================================

atexit.register(
    shutdown_camera
)


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":

    print()

    print("=" * 70)

    print(
        "AI EXAM SURVEILLANCE SYSTEM V2"
    )

    print("=" * 70)

    print(
        "Server        : "
        "http://127.0.0.1:5000"
    )

    print(
        "Camera source :",
        getattr(
            config,
            "CAMERA_SOURCE",
            "unknown"
        )
    )

    try:

        print(
            "Camera URL    :",
            config.get_camera_source()
        )

    except Exception:

        print(
            "Camera URL    :",
            "unknown"
        )

    try:

        print(
            "Models        :",
            config.check_models()
        )

    except Exception as e:

        print(
            "Models        :",
            "check failed:",
            e
        )

    print("=" * 70)
    print()


    try:

        app.run(

            host="127.0.0.1",

            port=5000,

            debug=False,

            threaded=True,

            use_reloader=False,

        )

    except KeyboardInterrupt:

        print()
        print(
            "Server stopped by user."
        )

    except Exception as e:

        print()
        print(
            "Flask application error:",
            e
        )

    finally:

        shutdown_camera()

        print(
            "Application shutdown complete."
        )
