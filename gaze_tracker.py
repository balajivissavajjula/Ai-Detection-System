# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# EYE GAZE DETECTION MODULE
# ============================================================

import cv2


# ============================================================
# CONFIGURATION
# ============================================================

# Gaze thresholds are normalized relative to face size
# instead of fixed pixel distances.

HORIZONTAL_THRESHOLD = 0.12
VERTICAL_THRESHOLD = 0.12


# ============================================================
# SAFE LANDMARK ACCESS
# ============================================================

def get_landmark(face, index):

    try:

        return face.landmark[index]

    except Exception:

        return None


# ============================================================
# DETECT GAZE
# ============================================================

def detect_gaze(
    frame,
    results
):
    """
    Estimate gaze direction from MediaPipe face landmarks.

    Returns:
        annotated_frame
        gaze_direction

    Possible directions:

        CENTER
        LEFT
        RIGHT
        UP
        DOWN
        NO FACE
    """

    # --------------------------------------------------------
    # Validate frame
    # --------------------------------------------------------

    if frame is None:

        return (
            frame,
            "NO FACE"
        )


    annotated_frame = frame.copy()


    gaze_direction = "CENTER"


    # --------------------------------------------------------
    # Validate MediaPipe results
    # --------------------------------------------------------

    if results is None:

        gaze_direction = "NO FACE"

        draw_gaze_status(
            annotated_frame,
            gaze_direction
        )

        return (
            annotated_frame,
            gaze_direction
        )


    try:

        faces = results.multi_face_landmarks

    except Exception:

        faces = None


    # --------------------------------------------------------
    # No face
    # --------------------------------------------------------

    if not faces:

        gaze_direction = "NO FACE"

        draw_gaze_status(
            annotated_frame,
            gaze_direction
        )

        return (
            annotated_frame,
            gaze_direction
        )


    # --------------------------------------------------------
    # Use first detected face
    # --------------------------------------------------------

    face = faces[0]


    # ========================================================
    # IMPORTANT MEDIAPIPE LANDMARKS
    # ========================================================

    # Left eye outer corner
    left_eye_outer = get_landmark(
        face,
        33
    )

    # Left eye inner corner
    left_eye_inner = get_landmark(
        face,
        133
    )

    # Right eye inner corner
    right_eye_inner = get_landmark(
        face,
        362
    )

    # Right eye outer corner
    right_eye_outer = get_landmark(
        face,
        263
    )

    # Nose
    nose = get_landmark(
        face,
        1
    )


    # --------------------------------------------------------
    # Make sure all landmarks exist
    # --------------------------------------------------------

    if any(
        landmark is None
        for landmark in (
            left_eye_outer,
            left_eye_inner,
            right_eye_inner,
            right_eye_outer,
            nose
        )
    ):

        gaze_direction = "CENTER"

        draw_gaze_status(
            annotated_frame,
            gaze_direction
        )

        return (
            annotated_frame,
            gaze_direction
        )


    # ========================================================
    # EYE CENTER
    # ========================================================

    left_eye_x = (
        left_eye_outer.x
        +
        left_eye_inner.x
    ) / 2.0

    left_eye_y = (
        left_eye_outer.y
        +
        left_eye_inner.y
    ) / 2.0


    right_eye_x = (
        right_eye_outer.x
        +
        right_eye_inner.x
    ) / 2.0

    right_eye_y = (
        right_eye_outer.y
        +
        right_eye_inner.y
    ) / 2.0


    eye_center_x = (
        left_eye_x
        +
        right_eye_x
    ) / 2.0


    eye_center_y = (
        left_eye_y
        +
        right_eye_y
    ) / 2.0


    # ========================================================
    # FACE WIDTH / HEIGHT
    # ========================================================

    try:

        face_xs = [
            lm.x
            for lm in face.landmark
        ]

        face_ys = [
            lm.y
            for lm in face.landmark
        ]

        face_width = (
            max(face_xs)
            -
            min(face_xs)
        )

        face_height = (
            max(face_ys)
            -
            min(face_ys)
        )

    except Exception:

        face_width = 0.0
        face_height = 0.0


    # --------------------------------------------------------
    # Prevent division by zero
    # --------------------------------------------------------

    if face_width <= 0:

        face_width = 0.20


    if face_height <= 0:

        face_height = 0.20


    # ========================================================
    # NOSE POSITION
    # ========================================================

    nose_x = nose.x

    nose_y = nose.y


    # --------------------------------------------------------
    # Relative displacement
    # --------------------------------------------------------

    dx = (
        nose_x
        -
        eye_center_x
    ) / face_width


    dy = (
        nose_y
        -
        eye_center_y
    ) / face_height


    # ========================================================
    # GAZE CLASSIFICATION
    # ========================================================

    # Horizontal direction gets priority because it is
    # generally more stable for this simple landmark method.

    if dx < -HORIZONTAL_THRESHOLD:

        gaze_direction = "LEFT"


    elif dx > HORIZONTAL_THRESHOLD:

        gaze_direction = "RIGHT"


    elif dy < -VERTICAL_THRESHOLD:

        gaze_direction = "UP"


    elif dy > VERTICAL_THRESHOLD:

        gaze_direction = "DOWN"


    else:

        gaze_direction = "CENTER"


    # ========================================================
    # DRAW GAZE
    # ========================================================

    draw_gaze_status(

        annotated_frame,

        gaze_direction

    )


    # ========================================================
    # DRAW REFERENCE POINTS
    # ========================================================

    try:

        height, width = (
            annotated_frame.shape[:2]
        )


        eye_x = int(
            eye_center_x * width
        )

        eye_y = int(
            eye_center_y * height
        )


        nose_px = int(
            nose_x * width
        )

        nose_py = int(
            nose_y * height
        )


        # Eye center
        cv2.circle(

            annotated_frame,

            (
                eye_x,
                eye_y
            ),

            3,

            (255, 255, 0),

            -1

        )


        # Nose point
        cv2.circle(

            annotated_frame,

            (
                nose_px,
                nose_py
            ),

            3,

            (0, 255, 255),

            -1

        )


        # Direction line
        cv2.line(

            annotated_frame,

            (
                eye_x,
                eye_y
            ),

            (
                nose_px,
                nose_py
            ),

            (255, 255, 0),

            1

        )

    except Exception:

        pass


    # ========================================================
    # RETURN
    # ========================================================

    return (

        annotated_frame,

        gaze_direction

    )


# ============================================================
# DRAW GAZE STATUS
# ============================================================

def draw_gaze_status(
    frame,
    gaze_direction
):

    if frame is None:

        return frame


    # --------------------------------------------------------
    # Position
    # --------------------------------------------------------

    x = 20
    y = 75


    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    text = (
        f"Eyes : {gaze_direction}"
    )


    # --------------------------------------------------------
    # Color
    # --------------------------------------------------------

    if gaze_direction == "CENTER":

        color = (
            0,
            255,
            0
        )

    elif gaze_direction == "NO FACE":

        color = (
            0,
            0,
            255
        )

    else:

        color = (
            0,
            255,
            255
        )


    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

    cv2.putText(

        frame,

        text,

        (
            x,
            y
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.70,

        color,

        2,

        cv2.LINE_AA

    )


    return frame


# ============================================================
# GET GAZE STATUS
# ============================================================

def get_gaze_status(
    gaze_direction
):

    if not gaze_direction:

        return "CENTER"


    return str(
        gaze_direction
    ).strip().upper()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("GAZE DETECTION MODULE")
    print("=" * 60)

    print(
        "Module loaded successfully."
    )

    print(
        "Horizontal threshold:",
        HORIZONTAL_THRESHOLD
    )

    print(
        "Vertical threshold:",
        VERTICAL_THRESHOLD
    )

    print()
    print(
        "Possible directions:"
    )

    print(
        "CENTER"
    )

    print(
        "LEFT"
    )

    print(
        "RIGHT"
    )

    print(
        "UP"
    )

    print(
        "DOWN"
    )

    print(
        "NO FACE"
    )

    print("=" * 60)