# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# FACE DETECTION MODULE
# ============================================================

import cv2


# ============================================================
# FACE DETECTION
# ============================================================

def detect_faces(
    frame,
    results
):
    """
    Detect and count faces using MediaPipe face results.

    Returns:
        annotated_frame
        face_count
        face_status
    """

    # --------------------------------------------------------
    # Validate frame
    # --------------------------------------------------------

    if frame is None:

        return (
            frame,
            0,
            "NO FACE"
        )


    # --------------------------------------------------------
    # Work on a copy so the original frame is not modified
    # unexpectedly by this module.
    # --------------------------------------------------------

    annotated_frame = frame.copy()


    face_count = 0

    face_status = "NO FACE"


    # --------------------------------------------------------
    # Validate MediaPipe results
    # --------------------------------------------------------

    if results is None:

        return (
            annotated_frame,
            face_count,
            face_status
        )


    # --------------------------------------------------------
    # Get face landmarks safely
    # --------------------------------------------------------

    try:

        face_landmarks_list = (
            results.multi_face_landmarks
        )

    except Exception:

        face_landmarks_list = None


    if not face_landmarks_list:

        return (
            annotated_frame,
            face_count,
            face_status
        )


    # --------------------------------------------------------
    # Face count
    # --------------------------------------------------------

    face_count = len(
        face_landmarks_list
    )


    # --------------------------------------------------------
    # Face status
    # --------------------------------------------------------

    if face_count == 1:

        face_status = "NORMAL"

    elif face_count > 1:

        face_status = "MULTIPLE FACES"


    # --------------------------------------------------------
    # Frame dimensions
    # --------------------------------------------------------

    try:

        height, width = (
            annotated_frame.shape[:2]
        )

    except Exception:

        return (
            annotated_frame,
            face_count,
            face_status
        )


    # ========================================================
    # DRAW EACH FACE
    # ========================================================

    for face_landmarks in face_landmarks_list:

        try:

            xs = []
            ys = []


            # ------------------------------------------------
            # Convert normalized MediaPipe coordinates
            # into pixel coordinates.
            # ------------------------------------------------

            for landmark in (
                face_landmarks.landmark
            ):

                x = int(
                    landmark.x * width
                )

                y = int(
                    landmark.y * height
                )


                # --------------------------------------------
                # Keep coordinates inside frame.
                # --------------------------------------------

                x = max(
                    0,
                    min(
                        width - 1,
                        x
                    )
                )

                y = max(
                    0,
                    min(
                        height - 1,
                        y
                    )
                )


                xs.append(x)
                ys.append(y)


            if not xs or not ys:

                continue


            # ------------------------------------------------
            # Bounding box
            # ------------------------------------------------

            x1 = min(xs)
            y1 = min(ys)

            x2 = max(xs)
            y2 = max(ys)


            # ------------------------------------------------
            # Add small padding around face.
            # ------------------------------------------------

            padding_x = int(
                (x2 - x1) * 0.08
            )

            padding_y = int(
                (y2 - y1) * 0.08
            )


            x1 = max(
                0,
                x1 - padding_x
            )

            y1 = max(
                0,
                y1 - padding_y
            )

            x2 = min(
                width - 1,
                x2 + padding_x
            )

            y2 = min(
                height - 1,
                y2 + padding_y
            )


            # ------------------------------------------------
            # Bounding box
            # ------------------------------------------------

            cv2.rectangle(

                annotated_frame,

                (x1, y1),

                (x2, y2),

                (0, 255, 0),

                2

            )


            # ------------------------------------------------
            # Face label
            # ------------------------------------------------

            label = face_status


            (
                text_width,
                text_height
            ), baseline = cv2.getTextSize(

                label,

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                1

            )


            text_y = max(
                y1 - 8,
                text_height + 5
            )


            # ------------------------------------------------
            # Label background
            # ------------------------------------------------

            cv2.rectangle(

                annotated_frame,

                (

                    x1,

                    text_y
                    - text_height
                    - 5

                ),

                (

                    x1
                    + text_width
                    + 6,

                    text_y
                    + baseline

                ),

                (0, 255, 0),

                -1

            )


            # ------------------------------------------------
            # Label text
            # ------------------------------------------------

            cv2.putText(

                annotated_frame,

                label,

                (

                    x1 + 3,

                    text_y - 3

                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                (255, 255, 255),

                1,

                cv2.LINE_AA

            )


        except Exception as e:

            print(
                "Face drawing error:",
                e
            )

            continue


    # ========================================================
    # FACE COUNT OVERLAY
    # ========================================================

    cv2.putText(

        annotated_frame,

        f"Faces: {face_count}",

        (15, 200),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (255, 255, 255),

        2,

        cv2.LINE_AA

    )


    # ========================================================
    # RETURN
    # ========================================================

    return (

        annotated_frame,

        face_count,

        face_status

    )


# ============================================================
# SIMPLE FACE STATUS HELPER
# ============================================================

def get_face_status(face_count):

    try:

        count = int(
            face_count
        )

    except Exception:

        count = 0


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
    print("FACE DETECTION MODULE")
    print("=" * 60)

    print(
        "Module loaded successfully."
    )

    print(
        "Status test:"
    )

    print(
        "0 faces  ->",
        get_face_status(0)
    )

    print(
        "1 face   ->",
        get_face_status(1)
    )

    print(
        "2 faces  ->",
        get_face_status(2)
    )

    print("=" * 60)