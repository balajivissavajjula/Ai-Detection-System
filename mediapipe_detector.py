# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# MEDIAPIPE FACE DETECTOR
# Compatible with MediaPipe 0.10.35
# ============================================================

import cv2
import mediapipe as mp


# ============================================================
# MEDIAPIPE TASKS
# ============================================================

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# CONFIGURATION
# ============================================================

FACE_MESH_MAX_FACES = 5

FACE_DETECTION_CONFIDENCE = 0.5
FACE_PRESENCE_CONFIDENCE = 0.5
FACE_TRACKING_CONFIDENCE = 0.5


# ============================================================
# NOTE
# ============================================================
#
# MediaPipe 0.10.35 does not provide:
#
#     mp.solutions.face_mesh
#
# The new MediaPipe Tasks API requires a .task model file.
#
# Since no .task file exists in the project or installed
# MediaPipe package, this module cannot initialize the
# Face Landmarker yet.
#
# This file therefore provides a safe interface so the
# remaining project can continue running.
#
# ============================================================


face_landmarker = None


# ============================================================
# INITIALIZE FACE LANDMARKER
# ============================================================

def initialize_face_mesh():

    global face_landmarker

    print()
    print("=" * 60)
    print("MEDIAPIPE FACE LANDMARKER")
    print("=" * 60)

    print(
        "MediaPipe version:",
        getattr(mp, "__version__", "unknown")
    )

    print(
        "API:",
        "MediaPipe Tasks"
    )

    print(
        "Status:",
        "WAITING FOR FACE LANDMARKER MODEL"
    )

    print(
        "No .task model file was found."
    )

    print("=" * 60)

    face_landmarker = None

    return False


# ============================================================
# DETECT FACE MESH
# ============================================================

def detect_face_mesh(frame):

    """
    Process one camera frame.

    Returns:
        MediaPipe result or None

    Until a compatible .task model is supplied,
    this safely returns None.
    """

    if frame is None:

        return None

    if face_landmarker is None:

        return None

    try:

        # Future MediaPipe Tasks implementation
        # will be connected here.

        return None

    except Exception as e:

        print(
            "Face landmark detection error:",
            e
        )

        return None


# ============================================================
# CLOSE FACE MESH
# ============================================================

def close_face_mesh():

    global face_landmarker

    try:

        if face_landmarker is not None:

            face_landmarker.close()

    except Exception as e:

        print(
            "Face Mesh close error:",
            e
        )

    finally:

        face_landmarker = None

    print(
        "Face Mesh released."
    )


# ============================================================
# GET FACE COUNT
# ============================================================

def get_face_count(results):

    if results is None:

        return 0

    try:

        # MediaPipe Tasks result
        if hasattr(
            results,
            "face_landmarks"
        ):

            return len(
                results.face_landmarks
            )

    except Exception:

        pass

    return 0


# ============================================================
# GET FACE STATUS
# ============================================================

def get_face_status(results):

    count = get_face_count(
        results
    )

    if count <= 0:

        return "NO FACE"

    if count == 1:

        return "NORMAL"

    return "MULTIPLE FACES"


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "MEDIAPIPE FACE DETECTOR TEST"
    )

    print("=" * 60)

    print(
        "MediaPipe version:",
        getattr(
            mp,
            "__version__",
            "unknown"
        )
    )

    print(
        "MediaPipe path:",
        mp.__file__
    )

    print()

    print(
        "Checking MediaPipe Tasks API..."
    )

    try:

        print(
            "mediapipe.tasks: OK"
        )

        print(
            "mediapipe.tasks.python: OK"
        )

        print(
            "mediapipe.tasks.python.vision: OK"
        )

    except Exception as e:

        print(
            "MediaPipe Tasks API error:",
            e
        )

    print()

    initialize_face_mesh()

    print()

    print(
        "Face count test:",
        get_face_count(None)
    )

    print(
        "Face status test:",
        get_face_status(None)
    )

    close_face_mesh()

    print()

    print("=" * 60)

    print(
        "MEDIAPIPE DETECTOR MODULE TEST COMPLETE"
    )

    print("=" * 60)