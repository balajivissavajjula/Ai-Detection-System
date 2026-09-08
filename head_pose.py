# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# HEAD POSE / HEAD DIRECTION DETECTION
# ============================================================

import cv2


# ============================================================
# CONFIGURATION
# ============================================================

# Normalized thresholds make detection less dependent on
# camera resolution and distance from the camera.

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
# DETECT HEAD POSE
# ============================================================

def detect_head_pose(
    frame,
    results
):

    """
    Detect approximate head direction using MediaPipe
    Face Mesh landmarks.

    Returns:

        annotated_frame
        head_direction

    Possible values:

        FORWARD
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


    head_direction = "FORWARD"


    # --------------------------------------------------------
    # Validate MediaPipe results
    # --------------------------------------------------------

    if results is None:

        head_direction = "NO FACE"

        draw_head_status(
            annotated_frame,
            head_direction
        )

        return (
            annotated_frame,
            head_direction
        )


    try:

        faces = results.multi_face_landmarks

    except Exception:

        faces = None


    # --------------------------------------------------------
    # No face
    # --------------------------------------------------------

    if not faces:

        head_direction = "NO FACE"

        draw_head_status(
            annotated_frame,
            head_direction
        )

        return (
            annotated_frame,
            head_direction
        )


    # --------------------------------------------------------
    # Use first face
    # --------------------------------------------------------

    face = faces[0]


    # ========================================================
    # MEDIAPIPE FACE LANDMARKS
    # ========================================================

    # Nose
    nose = get_landmark(
        face,
        1
    )

    # Left side of face
    left = get_landmark(
        face,
        234
    )

    # Right side of face
    right = get_landmark(
        face,
        454
    )

    # Top of head/face
    top = get_landmark(
        face,
        10
    )

    # Bottom of chin
    bottom = get_landmark(
        face,
        152
    )


    # --------------------------------------------------------
    # Check landmarks
    # --------------------------------------------------------

    if any(
        landmark is None
        for landmark in (
            nose,
            left,
            right,
            top,
            bottom
        )
    ):

        head_direction = "FORWARD"

        draw_head_status(
            annotated_frame,
            head_direction
        )

        return (
            annotated_frame,
            head_direction
        )


    # ========================================================
    # FACE CENTER
    # ========================================================

    center_x = (
        left.x
        +
        right.x
    ) / 2.0


    center_y = (
        top.y
        +
        bottom.y
    ) / 2.0


    # ========================================================
    # FACE DIMENSIONS
    # ========================================================

    face_width = (
        right.x
        -
        left.x
    )

    face_height = (
        bottom.y
        -
        top.y
    )


    # --------------------------------------------------------
    # Prevent invalid values
    # --------------------------------------------------------

    if face_width <= 0:

        face_width = 0.20


    if face_height <= 0:

        face_height = 0.30


    # ========================================================
    # NOSE DISPLACEMENT
    # ========================================================

    dx = (
        nose.x
        -
        center_x
    ) / face_width


    dy = (
        nose.y
        -
        center_y
    ) / face_height


    # ========================================================
    # HEAD DIRECTION
    # ========================================================

    # Horizontal direction

    if dx < -HORIZONTAL_THRESHOLD:

        head_direction = "LEFT"


    elif dx > HORIZONTAL_THRESHOLD:

        head_direction = "RIGHT"


    # Vertical direction

    elif dy < -VERTICAL_THRESHOLD:

        head_direction = "UP"


    elif dy > VERTICAL_THRESHOLD:

        head_direction = "DOWN"


    else:

        head_direction = "FORWARD"


    # ========================================================
    # DRAW STATUS
    # ========================================================

    draw_head_status(

        annotated_frame,

        head_direction

    )


    # ========================================================
    # DRAW FACE REFERENCE
    # ========================================================

    try:

        h, w = (
            annotated_frame.shape[:2]
        )


        # Nose point

        nose_x = int(
            nose.x * w
        )

        nose_y = int(
            nose.y * h
        )


        # Face center

        center_px = int(
            center_x * w
        )

        center_py = int(
            center_y * h
        )


        # Left face point

        left_px = int(
            left.x * w
        )

        left_py = int(
            left.y * h
        )


        # Right face point

        right_px = int(
            right.x * w
        )

        right_py = int(
            right.y * h
        )


        # Draw center point

        cv2.circle(

            annotated_frame,

            (
                center_px,
                center_py
            ),

            3,

            (255, 255, 0),

            -1

        )


        # Draw nose point

        cv2.circle(

            annotated_frame,

            (
                nose_x,
                nose_y
            ),

            4,

            (0, 255, 255),

            -1

        )


        # Draw face horizontal reference

        cv2.line(

            annotated_frame,

            (
                left_px,
                center_py
            ),

            (
                right_px,
                center_py
            ),

            (255, 255, 0),

            1

        )


        # Draw direction vector

        cv2.line(

            annotated_frame,

            (
                center_px,
                center_py
            ),

            (
                nose_x,
                nose_y
            ),

            (0, 255, 255),

            2

        )

    except Exception:

        pass


    # ========================================================
    # RETURN
    # ========================================================

    return (

        annotated_frame,

        head_direction

    )


# ============================================================
# DRAW HEAD STATUS
# ============================================================

def draw_head_status(
    frame,
    head_direction
):

    if frame is None:

        return frame


    text = (
        f"Head : {head_direction}"
    )


    # --------------------------------------------------------
    # Status color
    # --------------------------------------------------------

    if head_direction == "FORWARD":

        color = (
            0,
            255,
            0
        )

    elif head_direction == "NO FACE":

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
    # Draw text
    # --------------------------------------------------------

    cv2.putText(

        frame,

        text,

        (20, 40),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.70,

        color,

        2,

        cv2.LINE_AA

    )


    return frame


# ============================================================
# GET HEAD STATUS
# ============================================================

def get_head_status(
    head_direction
):

    if not head_direction:

        return "FORWARD"


    return str(
        head_direction
    ).strip().upper()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("HEAD POSE DETECTION MODULE")
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
        "FORWARD"
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