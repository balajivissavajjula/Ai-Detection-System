
# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# STUDENT TRACKING MODULE
# ============================================================

import math

from student_database import STUDENTS


# ============================================================
# TRACKING CONFIGURATION
# ============================================================

STUDENT_MATCH_DISTANCE = 80

students = {}

next_id = 1


# ============================================================
# GET STUDENT DETAILS
# ============================================================

def get_student_details(student_number):

    return STUDENTS.get(
        student_number,
        {
            "id": f"Student-{student_number}",
            "name": "Unknown",
            "branch": "-"
        }
    )


# ============================================================
# GET FACE BOUNDING BOX
# ============================================================

def get_face_bbox(frame, face):

    if frame is None or face is None:
        return None

    try:

        height, width = frame.shape[:2]

        xs = []
        ys = []

        for landmark in face.landmark:

            x = int(landmark.x * width)
            y = int(landmark.y * height)

            x = max(0, min(x, width - 1))
            y = max(0, min(y, height - 1))

            xs.append(x)
            ys.append(y)

        if not xs or not ys:
            return None

        return (
            min(xs),
            min(ys),
            max(xs),
            max(ys)
        )

    except Exception as e:

        print(
            "Face bbox error:",
            e
        )

        return None


# ============================================================
# FIND EXISTING STUDENT
# ============================================================

def find_existing_student(cx, cy, used_ids=None):

    if used_ids is None:
        used_ids = set()

    best_student = None
    best_distance = float("inf")

    for student_id, position in students.items():

        if student_id in used_ids:
            continue

        try:

            px, py = position

            distance = math.sqrt(
                (cx - px) ** 2 +
                (cy - py) ** 2
            )

            if (
                distance < STUDENT_MATCH_DISTANCE
                and distance < best_distance
            ):

                best_distance = distance
                best_student = student_id

        except Exception:
            continue

    return best_student


# ============================================================
# DRAW STUDENT INFORMATION
# ============================================================

def draw_student_info(
    frame,
    bbox,
    student,
    tracking_id
):

    if frame is None or bbox is None:
        return frame

    try:

        x1, y1, x2, y2 = bbox

        # ----------------------------------------------------
        # Face box
        # ----------------------------------------------------

        cv2_color = (0, 255, 0)

        import cv2

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            cv2_color,
            2
        )

        # ----------------------------------------------------
        # Text position
        # ----------------------------------------------------

        text_x = x1

        text_y = max(
            20,
            y1 - 10
        )

        # ----------------------------------------------------
        # Student label
        # ----------------------------------------------------

        label = (
            f"{student['name']} | "
            f"{student['id']} | "
            f"{student.get('branch', '-')}"
        )

        # ----------------------------------------------------
        # Tracking label
        # ----------------------------------------------------

        tracking_label = (
            f"Tracking ID: {tracking_id}"
        )

        # ----------------------------------------------------
        # Background
        # ----------------------------------------------------

        (
            width1,
            height1
        ), baseline1 = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            1
        )

        cv2.rectangle(
            frame,
            (
                text_x,
                max(
                    0,
                    text_y - height1 - 8
                )
            ),
            (
                text_x + width1 + 8,
                text_y + baseline1
            ),
            (0, 0, 0),
            -1
        )

        # ----------------------------------------------------
        # Student text
        # ----------------------------------------------------

        cv2.putText(
            frame,
            label,
            (
                text_x + 4,
                text_y
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (0, 255, 255),
            1,
            cv2.LINE_AA
        )

        # ----------------------------------------------------
        # Tracking ID
        # ----------------------------------------------------

        cv2.putText(
            frame,
            tracking_label,
            (
                x1,
                min(
                    frame.shape[0] - 10,
                    y2 + 18
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    except Exception as e:

        print(
            "Student drawing error:",
            e
        )

    return frame


# ============================================================
# ASSIGN STUDENT IDs
# ============================================================

def assign_student_ids(frame, results):

    global students
    global next_id

    if frame is None:
        return frame

    # --------------------------------------------------------
    # No faces
    # --------------------------------------------------------

    if (
        results is None
        or not getattr(
            results,
            "multi_face_landmarks",
            None
        )
    ):

        students = {}

        return frame

    updated_students = {}

    used_ids = set()

    # ========================================================
    # PROCESS FACES
    # ========================================================

    for face in results.multi_face_landmarks:

        bbox = get_face_bbox(
            frame,
            face
        )

        if bbox is None:
            continue

        x1, y1, x2, y2 = bbox

        # ----------------------------------------------------
        # Face center
        # ----------------------------------------------------

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        # ----------------------------------------------------
        # Match previous tracking ID
        # ----------------------------------------------------

        assigned_id = find_existing_student(
            cx,
            cy,
            used_ids
        )

        # ----------------------------------------------------
        # New tracking ID
        # ----------------------------------------------------

        if assigned_id is None:

            assigned_id = next_id

            next_id += 1

        used_ids.add(
            assigned_id
        )

        # ----------------------------------------------------
        # Save current position
        # ----------------------------------------------------

        updated_students[
            assigned_id
        ] = (
            cx,
            cy
        )

        # ----------------------------------------------------
        # Get virtual student details
        # ----------------------------------------------------

        student = get_student_details(
            assigned_id
        )

        # ----------------------------------------------------
        # Draw student information
        # ----------------------------------------------------

        draw_student_info(
            frame,
            bbox,
            student,
            assigned_id
        )

    # ========================================================
    # UPDATE TRACKING STATE
    # ========================================================

    students = updated_students

    return frame


# ============================================================
# RESET TRACKING
# ============================================================

def reset_student_tracking():

    global students
    global next_id

    students = {}

    next_id = 1


# ============================================================
# GET TRACKED STUDENTS
# ============================================================

def get_tracked_students():

    tracked = []

    for tracking_id in sorted(
        students.keys()
    ):

        student = get_student_details(
            tracking_id
        )

        tracked.append({

            "tracking_id":
                tracking_id,

            "student_id":
                student.get(
                    "id",
                    f"Student-{tracking_id}"
                ),

            "name":
                student.get(
                    "name",
                    "Unknown"
                ),

            "branch":
                student.get(
                    "branch",
                    "-"
                )

        })

    return tracked


# ============================================================
# GET STUDENT COUNT
# ============================================================

def get_student_count():

    return len(
        students
    )


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("STUDENT TRACKING MODULE TEST")
    print("=" * 60)

    print(
        "Known students:",
        len(STUDENTS)
    )

    print(
        "Match distance:",
        STUDENT_MATCH_DISTANCE
    )

    print(
        "Initial tracked students:",
        get_student_count()
    )

    print()

    print("Virtual student mapping:")

    for number, student in STUDENTS.items():

        details = get_student_details(
            number
        )

        print(
            f"{number} -> "
            f"{details['id']} | "
            f"{details['name']} | "
            f"{details.get('branch', '-')}"
        )

    print()

    print(
        "Resetting tracking..."
    )

    reset_student_tracking()

    print(
        "Tracked students after reset:",
        get_student_count()
    )

    print()

    print(
        "STUDENT TRACKING MODULE OK"
    )

    print("=" * 60)
