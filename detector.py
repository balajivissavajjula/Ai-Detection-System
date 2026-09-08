
# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# YOLO DETECTOR
#
# SEPARATED DETECTION ARCHITECTURE
# ------------------------------------------------------------
# BOOK + PHONE MODEL
#   -> book
#   -> phone
#
# PAPER + FACE + HAND MODEL
#   -> paper
#   -> Face
#   -> hand classes
#
# EXAM BEHAVIOR MODEL
#   -> cheating
#   -> normal
#   -> cheat_paper
#   -> look_around
#   -> use_phone
#
# OBJECT MODEL
#   -> calculator
#   -> earphone
#   -> sunglasses
#   -> watch
#
# IMPORTANT
# ------------------------------------------------------------
# Behavior labels NEVER directly become physical-object flags.
#
# use_phone  != phone_detected
# cheat_paper != paper_detected
#
# Physical flags come only from the correct physical-object
# model.
#
# Temporal confirmation is performed per fresh AI inference
# cycle, not per cached/displayed camera frame.
# ============================================================

from ultralytics import YOLO

import cv2
import time
from pathlib import Path

import config

from screenshot import save_screenshot
from logger import log_violation


# ============================================================
# MODEL PATHS
# ============================================================

MODEL_PATHS = config.get_model_paths()


# ============================================================
# DEVICE
# ============================================================

try:

    import torch

    configured_device = str(
        getattr(
            config,
            "YOLO_DEVICE",
            "cpu"
        )
    ).lower()

    if configured_device not in {
        "cpu",
        "cuda",
    }:

        configured_device = "cpu"


    if (
        configured_device == "cuda"
        and torch.cuda.is_available()
    ):

        DEVICE = 0
        DEVICE_NAME = "cuda"

    else:

        DEVICE = "cpu"
        DEVICE_NAME = "cpu"

except Exception:

    DEVICE = "cpu"
    DEVICE_NAME = "cpu"


# ============================================================
# PERFORMANCE
# ============================================================

DETECTION_INTERVAL = max(
    1,
    int(
        getattr(
            config,
            "DETECT_EVERY_N_FRAMES",
            4
        )
    )
)


INFERENCE_SIZE = int(
    getattr(
        config,
        "YOLO_INFERENCE_SIZE",
        getattr(
            config,
            "YOLO_IMAGE_SIZE",
            320
        )
    )
)


MAX_DETECTIONS = int(
    getattr(
        config,
        "YOLO_MAX_DETECTIONS",
        50
    )
)


# ============================================================
# MODEL-SPECIFIC CONFIDENCE
#
# Read from config.py so there is only one source of truth.
# ============================================================

BOOK_PHONE_CONFIDENCE = float(
    getattr(
        config,
        "BOOK_PHONE_CONFIDENCE",
        0.60
    )
)


BEHAVIOR_CONFIDENCE = float(
    getattr(
        config,
        "EXAM_BEHAVIOR_CONFIDENCE",
        0.65
    )
)


FACE_HAND_CONFIDENCE = float(
    getattr(
        config,
        "PAPER_FACE_HAND_CONFIDENCE",
        0.60
    )
)


OBJECT_CONFIDENCE = float(
    getattr(
        config,
        "OBJECT_CONFIDENCE",
        0.65
    )
)


# ============================================================
# TEMPORAL CONFIRMATION
# ============================================================

OBJECT_CONFIRM_FRAMES = max(
    1,
    int(
        getattr(
            config,
            "OBJECT_CONFIRM_FRAMES",
            3
        )
    )
)


BEHAVIOR_CONFIRM_FRAMES = max(
    1,
    int(
        getattr(
            config,
            "BEHAVIOR_CONFIRM_FRAMES",
            3
        )
    )
)


# ============================================================
# DETECTION TIMEOUT
# ============================================================

DETECTION_TIMEOUT = float(
    getattr(
        config,
        "DETECTION_TIMEOUT",
        1.0
    )
)


# ============================================================
# VIOLATION COOLDOWN
# ============================================================

VIOLATION_COOLDOWN = float(
    getattr(
        config,
        "violation_cooldown",
        5
    )
)


# ============================================================
# DUPLICATE IOU
# ============================================================

DUPLICATE_IOU_THRESHOLD = 0.50


# ============================================================
# MODEL-SPECIFIC LABELS
# ============================================================

BOOK_PHONE_LABELS = {
    "book",
    "phone",
}


BEHAVIOR_LABELS = {
    "cheating",
    "normal",
    "cheat_paper",
    "look_around",
    "use_phone",
}


FACE_HAND_LABELS = {
    "paper",
    "face",
    "fist",
    "index_left",
    "index_right",
    "open_palm",
    "point",
    "thumbs_down",
    "thumbs_up",
}


OBJECT_MODEL_LABELS = {
    "calculator",
    "earphone",
    "sunglasses",
    "watch",
}


# ============================================================
# PHYSICAL RESTRICTED OBJECTS
#
# This is the complete physical-object set.
# ============================================================

PHYSICAL_RESTRICTED_OBJECTS = {
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

BEHAVIOR_VIOLATIONS = set(
    getattr(
        config,
        "BEHAVIOR_VIOLATIONS",
        {
            "cheating",
            "cheat_paper",
            "look_around",
            "use_phone",
        }
    )
)


# ============================================================
# STATE
# ============================================================

_frame_counter = 0

_last_results = []

_last_detection_time = 0.0

_last_inference_frame = 0


# ============================================================
# VIOLATION STATE
# ============================================================

_last_violation_time = {}


# ============================================================
# OBJECT TEMPORAL STATE
# ============================================================

_object_candidate_counts = {}

_object_last_seen_inference = {}


# ============================================================
# BEHAVIOR TEMPORAL STATE
# ============================================================

_behavior_candidate = ""

_behavior_candidate_count = 0

_behavior_last_seen_inference = 0


# ============================================================
# FPS
# ============================================================

_fps = 0.0

_fps_counter = 0

_fps_start_time = time.time()

_last_inference_ms = 0.0


# ============================================================
# MODELS
# ============================================================

print()
print("=" * 70)
print("YOLO DEVICE :", DEVICE_NAME.upper())
print("=" * 70)

print()
print("=" * 70)
print("LOADING YOLO MODELS")
print("=" * 70)


models = {}


# ============================================================
# MODEL LOADER
# ============================================================

def load_model(name, path):

    print()
    print(name.upper())
    print("-" * 50)

    print("Path:", path)

    try:

        path = Path(path)

    except Exception:

        print("ERROR: Invalid model path.")

        return None


    if not path.exists():

        print("ERROR: Model not found!")

        return None


    try:

        model = YOLO(
            str(path)
        )

        print(
            "Classes:",
            model.names
        )

        return model

    except Exception as e:

        print(
            "ERROR loading model:",
            e
        )

        return None


# ============================================================
# LOAD MODELS
# ============================================================

models["book_phone"] = load_model(
    "Book + Phone Model",
    MODEL_PATHS["book_phone"]
)


models["exam_behavior"] = load_model(
    "Exam Behavior Model",
    MODEL_PATHS["exam_behavior"]
)


models["paper_face_hand"] = load_model(
    "Paper + Face + Hand Model",
    MODEL_PATHS["paper_face_hand"]
)


if "object" in MODEL_PATHS:

    models["object"] = load_model(
        "Object Model",
        MODEL_PATHS["object"]
    )


# ============================================================
# MODEL SUMMARY
# ============================================================

print()
print("=" * 70)
print("YOLO MODELS LOADED")
print("=" * 70)

for name, model in models.items():

    print(
        f"  {name}:",
        "OK"
        if model is not None
        else "FAILED"
    )


print()

print(
    "Inference device       :",
    DEVICE_NAME
)

print(
    "Inference size         :",
    INFERENCE_SIZE
)

print(
    "Detection interval     :",
    DETECTION_INTERVAL
)

print(
    "Book/Phone confidence  :",
    BOOK_PHONE_CONFIDENCE
)

print(
    "Behavior confidence    :",
    BEHAVIOR_CONFIDENCE
)

print(
    "Face/Hand confidence   :",
    FACE_HAND_CONFIDENCE
)

print(
    "Object confidence      :",
    OBJECT_CONFIDENCE
)

print(
    "Object confirmation    :",
    OBJECT_CONFIRM_FRAMES
)

print(
    "Behavior confirmation  :",
    BEHAVIOR_CONFIRM_FRAMES
)

print(
    "Detection timeout      :",
    DETECTION_TIMEOUT
)

print(
    "Violation cooldown     :",
    VIOLATION_COOLDOWN
)

print("=" * 70)


# ============================================================
# LABEL HELPER
# ============================================================

def get_label(model, cls):

    try:

        names = model.names

        if isinstance(names, dict):

            return str(
                names.get(
                    cls,
                    str(cls)
                )
            )


        if isinstance(names, list):

            if 0 <= cls < len(names):

                return str(
                    names[cls]
                )

    except Exception:

        pass


    return str(cls)


# ============================================================
# NORMALIZE LABEL
# ============================================================

def normalize_label(label):

    return str(
        label
    ).strip().lower()


# ============================================================
# MODEL CONFIDENCE
# ============================================================

def get_model_confidence(model_name):

    if model_name == "book_phone":

        return BOOK_PHONE_CONFIDENCE


    if model_name == "exam_behavior":

        return BEHAVIOR_CONFIDENCE


    if model_name == "paper_face_hand":

        return FACE_HAND_CONFIDENCE


    if model_name == "object":

        return OBJECT_CONFIDENCE


    return float(
        getattr(
            config,
            "YOLO_CONFIDENCE",
            0.30
        )
    )


# ============================================================
# EXPECTED LABELS FOR MODEL
# ============================================================

def get_allowed_model_labels(model_name):

    if model_name == "book_phone":

        return BOOK_PHONE_LABELS


    if model_name == "exam_behavior":

        return BEHAVIOR_LABELS


    if model_name == "paper_face_hand":

        return FACE_HAND_LABELS


    if model_name == "object":

        return OBJECT_MODEL_LABELS


    return set()


# ============================================================
# BOX VALIDATION
# ============================================================

def valid_box(box):

    try:

        x1, y1, x2, y2 = box

        if x2 <= x1:

            return False

        if y2 <= y1:

            return False

        return True

    except Exception:

        return False


# ============================================================
# BOX AREA RATIO
# ============================================================

def box_area_ratio(box, frame):

    try:

        x1, y1, x2, y2 = box

        width = max(
            0,
            x2 - x1
        )

        height = max(
            0,
            y2 - y1
        )

        box_area = width * height

        frame_area = (
            frame.shape[0]
            * frame.shape[1]
        )

        if frame_area <= 0:

            return 0.0

        return (
            box_area
            / frame_area
        )

    except Exception:

        return 0.0


# ============================================================
# RUN ONE MODEL
# ============================================================

def run_model(
    model_name,
    model,
    frame
):

    detections = []


    if model is None:

        return detections


    confidence_threshold = (
        get_model_confidence(
            model_name
        )
    )


    allowed_labels = (
        get_allowed_model_labels(
            model_name
        )
    )


    try:

        results = model.predict(

            source=frame,

            imgsz=INFERENCE_SIZE,

            conf=confidence_threshold,

            max_det=MAX_DETECTIONS,

            device=DEVICE,

            verbose=False,

            stream=False,

        )

    except Exception as e:

        print(
            f"YOLO error [{model_name}]:",
            e
        )

        return detections


    for result in results:

        if result is None:

            continue


        if result.boxes is None:

            continue


        for box in result.boxes:

            try:

                confidence = float(
                    box.conf[0]
                )

                cls = int(
                    box.cls[0]
                )

                coordinates = (
                    box.xyxy[0]
                    .tolist()
                )

                x1, y1, x2, y2 = map(
                    int,
                    coordinates
                )

            except Exception:

                continue


            current_box = (
                x1,
                y1,
                x2,
                y2
            )


            if not valid_box(
                current_box
            ):

                continue


            label = get_label(
                model,
                cls
            )


            normalized = normalize_label(
                label
            )


            # ------------------------------------------------
            # Model isolation.
            # ------------------------------------------------

            if normalized not in allowed_labels:

                continue


            detections.append({

                "model":
                    model_name,

                "label":
                    label,

                "normalized":
                    normalized,

                "confidence":
                    confidence,

                "box":
                    current_box,

                "area_ratio":
                    box_area_ratio(
                        current_box,
                        frame
                    ),

            })


    return detections


# ============================================================
# RUN ALL MODELS
# ============================================================

def run_all_models(frame):

    global _last_inference_ms

    all_detections = []

    start_time = time.perf_counter()


    # --------------------------------------------------------
    # 1. BOOK + PHONE
    # --------------------------------------------------------

    model = models.get(
        "book_phone"
    )

    if model is not None:

        all_detections.extend(

            run_model(
                "book_phone",
                model,
                frame
            )

        )


    # --------------------------------------------------------
    # 2. EXAM BEHAVIOR
    # --------------------------------------------------------

    model = models.get(
        "exam_behavior"
    )

    if model is not None:

        all_detections.extend(

            run_model(
                "exam_behavior",
                model,
                frame
            )

        )


    # --------------------------------------------------------
    # 3. PAPER + FACE + HAND
    # --------------------------------------------------------

    model = models.get(
        "paper_face_hand"
    )

    if model is not None:

        all_detections.extend(

            run_model(
                "paper_face_hand",
                model,
                frame
            )

        )


    # --------------------------------------------------------
    # 4. OBJECT MODEL
    # --------------------------------------------------------

    model = models.get(
        "object"
    )

    if model is not None:

        all_detections.extend(

            run_model(
                "object",
                model,
                frame
            )

        )


    _last_inference_ms = (

        time.perf_counter()
        - start_time

    ) * 1000


    return all_detections


# ============================================================
# IOU
# ============================================================

def calculate_iou(
    box1,
    box2
):

    try:

        x1 = max(
            box1[0],
            box2[0]
        )

        y1 = max(
            box1[1],
            box2[1]
        )

        x2 = min(
            box1[2],
            box2[2]
        )

        y2 = min(
            box1[3],
            box2[3]
        )


        width = max(
            0,
            x2 - x1
        )

        height = max(
            0,
            y2 - y1
        )


        intersection = (
            width * height
        )


        area1 = (

            max(
                0,
                box1[2] - box1[0]
            )

            *

            max(
                0,
                box1[3] - box1[1]
            )

        )


        area2 = (

            max(
                0,
                box2[2] - box2[0]
            )

            *

            max(
                0,
                box2[3] - box2[1]
            )

        )


        union = (
            area1
            + area2
            - intersection
        )


        if union <= 0:

            return 0.0


        return (
            intersection
            / union
        )

    except Exception:

        return 0.0


# ============================================================
# REMOVE DUPLICATES
#
# Detections from different models remain independent.
# ============================================================

def remove_duplicate_detections(
    detections
):

    if not detections:

        return []


    final = []


    sorted_detections = sorted(

        detections,

        key=lambda item:
            item.get(
                "confidence",
                0
            ),

        reverse=True

    )


    for detection in sorted_detections:

        label = normalize_label(

            detection.get(
                "label",
                ""
            )

        )


        model_name = detection.get(
            "model",
            ""
        )


        box = detection.get(
            "box",
            None
        )


        if not box:

            continue


        duplicate = False


        for existing in final:

            existing_label = (
                normalize_label(
                    existing.get(
                        "label",
                        ""
                    )
                )
            )


            existing_model = (
                existing.get(
                    "model",
                    ""
                )
            )


            # Different models are independent.
            if model_name != existing_model:

                continue


            if label != existing_label:

                continue


            existing_box = existing.get(
                "box",
                None
            )


            if not existing_box:

                continue


            if calculate_iou(
                box,
                existing_box
            ) >= DUPLICATE_IOU_THRESHOLD:

                duplicate = True

                break


        if not duplicate:

            final.append(
                detection
            )


    return final


# ============================================================
# KEEP BEST PER MODEL + LABEL
# ============================================================

def keep_best_per_model_label(
    detections
):

    best = {}


    for detection in detections:

        model_name = detection.get(
            "model",
            ""
        )


        label = normalize_label(

            detection.get(
                "label",
                ""
            )

        )


        confidence = float(

            detection.get(
                "confidence",
                0
            )

        )


        key = (
            model_name,
            label
        )


        if (

            key not in best

            or

            confidence
            >
            best[key]["confidence"]

        ):

            best[key] = detection


    return list(
        best.values()
    )


# ============================================================
# RESET LIVE FLAGS
# ============================================================

def reset_live_flags():

    config.paper_detected = False

    config.phone_detected = False

    config.book_detected = False

    config.calculator_detected = False

    config.earphone_detected = False

    config.sunglasses_detected = False

    config.watch_detected = False

    config.face_count = 0

    config.face_status = "NO FACE"

    config.detected_objects = []

    config.detected_restricted_objects = []


# ============================================================
# UPDATE PHYSICAL FLAGS
#
# ONLY the correct physical-object model can update each flag.
#
# book/phone -> book_phone model
# paper       -> paper_face_hand model
# calculator  -> object model
# earphone    -> object model
# sunglasses  -> object model
# watch       -> object model
# ============================================================

def update_physical_flags(
    detections
):

    face_count = 0


    detected_objects = []

    restricted_objects = []


    for detection in detections:

        model_name = detection.get(
            "model",
            ""
        )


        label = normalize_label(

            detection.get(
                "label",
                ""
            )

        )


        # ----------------------------------------------------
        # BOOK + PHONE MODEL
        # ----------------------------------------------------

        if model_name == "book_phone":

            if label == "phone":

                config.phone_detected = True

                detected_objects.append(
                    "phone"
                )


            elif label == "book":

                config.book_detected = True

                detected_objects.append(
                    "book"
                )


        # ----------------------------------------------------
        # PAPER + FACE + HAND MODEL
        # ----------------------------------------------------

        elif model_name == "paper_face_hand":

            if label == "paper":

                config.paper_detected = True

                detected_objects.append(
                    "paper"
                )


            elif label == "face":

                face_count += 1


        # ----------------------------------------------------
        # OBJECT MODEL
        # ----------------------------------------------------

        elif model_name == "object":

            if label == "calculator":

                config.calculator_detected = True

                detected_objects.append(
                    "calculator"
                )


            elif label == "earphone":

                config.earphone_detected = True

                detected_objects.append(
                    "earphone"
                )


            elif label == "sunglasses":

                config.sunglasses_detected = True

                detected_objects.append(
                    "sunglasses"
                )


            elif label == "watch":

                config.watch_detected = True

                detected_objects.append(
                    "watch"
                )


    # --------------------------------------------------------
    # FACE
    # --------------------------------------------------------

    config.face_count = face_count


    if face_count > 0:

        config.face_status = "FACE DETECTED"

    else:

        config.face_status = "NO FACE"


    # --------------------------------------------------------
    # Remove duplicates.
    # --------------------------------------------------------

    detected_objects = list(
        dict.fromkeys(
            detected_objects
        )
    )


    # --------------------------------------------------------
    # Restricted physical objects.
    # --------------------------------------------------------

    restricted_objects = [

        item

        for item in detected_objects

        if item in PHYSICAL_RESTRICTED_OBJECTS

    ]


    config.detected_objects = (
        detected_objects
    )

    config.detected_restricted_objects = (
        restricted_objects
    )


# ============================================================
# RESET BEHAVIOR
# ============================================================

def reset_behavior_state():

    global _behavior_candidate
    global _behavior_candidate_count
    global _behavior_last_seen_inference

    _behavior_candidate = ""

    _behavior_candidate_count = 0

    _behavior_last_seen_inference = 0


    config.behavior_status = "NORMAL"

    config.behavior_score = 0

    config.behavior_reasons = []


# ============================================================
# UPDATE BEHAVIOR
#
# Behavior model is completely independent from physical
# object flags.
# ============================================================

def update_behavior(
    detections,
    inference_number
):

    global _behavior_candidate
    global _behavior_candidate_count
    global _behavior_last_seen_inference


    behavior_detections = [

        detection

        for detection in detections

        if detection.get("model")
        == "exam_behavior"

        and normalize_label(
            detection.get(
                "label",
                ""
            )
        )
        in BEHAVIOR_LABELS

    ]


    if not behavior_detections:

        return None


    # --------------------------------------------------------
    # Pick strongest behavior prediction.
    # --------------------------------------------------------

    strongest = max(

        behavior_detections,

        key=lambda item:
            float(
                item.get(
                    "confidence",
                    0
                )
            )

    )


    label = normalize_label(

        strongest.get(
            "label",
            ""
        )

    )


    confidence = float(

        strongest.get(
            "confidence",
            0
        )

    )


    # --------------------------------------------------------
    # NORMAL
    # --------------------------------------------------------

    if label == "normal":

        _behavior_candidate = ""

        _behavior_candidate_count = 0

        _behavior_last_seen_inference = (
            inference_number
        )

        config.behavior_status = "NORMAL"

        config.behavior_score = 0

        config.behavior_reasons = []

        return strongest


    # --------------------------------------------------------
    # Unknown / non-violation behavior.
    # --------------------------------------------------------

    if label not in BEHAVIOR_VIOLATIONS:

        return strongest


    # --------------------------------------------------------
    # Break old sequence if an inference cycle was missed.
    # --------------------------------------------------------

    if (

        _behavior_last_seen_inference > 0

        and

        inference_number
        - _behavior_last_seen_inference
        > 1

    ):

        _behavior_candidate = ""

        _behavior_candidate_count = 0


    # --------------------------------------------------------
    # Confirmation sequence.
    # --------------------------------------------------------

    if label == _behavior_candidate:

        _behavior_candidate_count += 1

    else:

        _behavior_candidate = label

        _behavior_candidate_count = 1


    _behavior_last_seen_inference = (
        inference_number
    )


    config.behavior_status = label.upper()

    config.behavior_score = int(
        confidence * 100
    )

    config.behavior_reasons = [
        label
    ]


    print(
        "BEHAVIOR VERIFY | "
        f"{label} | "
        f"{_behavior_candidate_count}/"
        f"{BEHAVIOR_CONFIRM_FRAMES} | "
        f"confidence={confidence:.2f}"
    )


    return strongest


# ============================================================
# RESET OBJECT TEMPORAL STATE
# ============================================================

def reset_object_state():

    global _object_candidate_counts
    global _object_last_seen_inference

    _object_candidate_counts = {}

    _object_last_seen_inference = {}


# ============================================================
# UPDATE OBJECT TEMPORAL STATE
# ============================================================

def update_object_confirmation(
    detections,
    inference_number
):

    current_objects = set()


    # --------------------------------------------------------
    # Only physical restricted objects participate.
    #
    # Behavior model is explicitly ignored.
    # --------------------------------------------------------

    for detection in detections:

        model_name = detection.get(
            "model",
            ""
        )


        label = normalize_label(

            detection.get(
                "label",
                ""
            )

        )


        if model_name == "exam_behavior":

            continue


        if label not in PHYSICAL_RESTRICTED_OBJECTS:

            continue


        current_objects.add(
            label
        )


    # --------------------------------------------------------
    # Update present objects.
    # --------------------------------------------------------

    for label in current_objects:

        previous_inference = (
            _object_last_seen_inference.get(
                label,
                0
            )
        )


        # If object disappeared for an AI cycle,
        # restart confirmation.
        if (

            previous_inference > 0

            and

            inference_number
            - previous_inference
            > 1

        ):

            _object_candidate_counts[label] = 1

        else:

            _object_candidate_counts[label] = (

                _object_candidate_counts.get(
                    label,
                    0
                )

                + 1

            )


        _object_last_seen_inference[label] = (
            inference_number
        )


        count = _object_candidate_counts[label]


        print(
            "OBJECT VERIFY | "
            f"{label} | "
            f"{count}/"
            f"{OBJECT_CONFIRM_FRAMES}"
        )


    # --------------------------------------------------------
    # Remove objects not present in this AI cycle.
    # --------------------------------------------------------

    for label in list(
        _object_candidate_counts.keys()
    ):

        if label not in current_objects:

            _object_candidate_counts.pop(
                label,
                None
            )

            _object_last_seen_inference.pop(
                label,
                None
            )


    return current_objects


# ============================================================
# GET STRONGEST DETECTION
# ============================================================

def get_strongest_detection(
    detections,
    label
):

    target = normalize_label(
        label
    )


    matches = [

        detection

        for detection in detections

        if normalize_label(
            detection.get(
                "label",
                ""
            )
        )
        == target

    ]


    if not matches:

        return None


    return max(

        matches,

        key=lambda item:
            float(
                item.get(
                    "confidence",
                    0
                )
            )

    )


# ============================================================
# REGISTER VIOLATION
# ============================================================

def register_violation(
    label,
    confidence,
    frame
):

    global _last_violation_time


    if not config.exam_started:

        return False


    label_key = normalize_label(
        label
    )


    now = time.time()


    previous_time = (
        _last_violation_time.get(
            label_key,
            0
        )
    )


    # --------------------------------------------------------
    # Same-label cooldown.
    # --------------------------------------------------------

    if (

        now - previous_time
        < VIOLATION_COOLDOWN

    ):

        return False


    _last_violation_time[
        label_key
    ] = now


    # --------------------------------------------------------
    # UPDATE CONFIG
    # --------------------------------------------------------

    config.total_violations += 1

    config.violations = (
        config.total_violations
    )

    config.last_violation_time = now

    config.current_detected_object = label

    config.last_detected_object = label

    config.current_status = "VIOLATION"


    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    if getattr(
        config,
        "SAVE_VIOLATION_SCREENSHOTS",
        True
    ):

        try:

            save_screenshot(
                frame,
                label
            )

            print(
                "SCREENSHOT SAVED | "
                f"Confirmed violation: {label}"
            )

        except Exception as e:

            print(
                "Screenshot error:",
                e
            )


    # --------------------------------------------------------
    # LOGGER
    # --------------------------------------------------------

    try:

        log_violation(
            label,
            "VIOLATION"
        )

    except Exception as e:

        print(
            "Logger error:",
            e
        )


    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print(
        "=" * 60
    )

    print(
        "CONFIRMED VIOLATION"
    )

    print(
        "Label      :",
        label
    )

    print(
        "Confidence :",
        f"{confidence:.2f}"
    )

    print(
        "Total      :",
        config.total_violations
    )

    print(
        "=" * 60
    )


    return True


# ============================================================
# PROCESS CONFIRMED VIOLATIONS
#
# Called ONLY on a fresh AI inference.
# ============================================================

def process_confirmed_violations(
    detections,
    frame,
    inference_number
):

    if not config.exam_started:

        return


    # ========================================================
    # PHYSICAL OBJECTS
    # ========================================================

    current_objects = (
        update_object_confirmation(
            detections,
            inference_number
        )
    )


    for label in current_objects:

        count = (
            _object_candidate_counts.get(
                label,
                0
            )
        )


        if count < OBJECT_CONFIRM_FRAMES:

            continue


        detection = (
            get_strongest_detection(
                detections,
                label
            )
        )


        if detection is None:

            continue


        confidence = float(

            detection.get(
                "confidence",
                0
            )

        )


        register_violation(

            label,

            confidence,

            frame

        )


    # ========================================================
    # BEHAVIOR
    # ========================================================

    behavior_detection = (
        update_behavior(
            detections,
            inference_number
        )
    )


    if behavior_detection is None:

        return


    behavior_label = normalize_label(

        behavior_detection.get(
            "label",
            ""
        )

    )


    if behavior_label not in BEHAVIOR_VIOLATIONS:

        return


    if (

        _behavior_candidate_count
        < BEHAVIOR_CONFIRM_FRAMES

    ):

        return


    confidence = float(

        behavior_detection.get(
            "confidence",
            0
        )

    )


    register_violation(

        behavior_label,

        confidence,

        frame

    )


# ============================================================
# UPDATE LAST DETECTED OBJECT
#
# Display information only.
# It does NOT create violations.
# ============================================================

def update_last_detected_object(
    detections
):

    physical_labels = []

    behavior_labels = []


    for detection in detections:

        model_name = detection.get(
            "model",
            ""
        )


        label = detection.get(
            "label",
            ""
        )


        normalized = normalize_label(
            label
        )


        if model_name == "exam_behavior":

            if normalized != "normal":

                behavior_labels.append(
                    label
                )


        elif normalized in PHYSICAL_RESTRICTED_OBJECTS:

            physical_labels.append(
                label
            )


    # --------------------------------------------------------
    # Physical objects first.
    # --------------------------------------------------------

    combined = []

    combined.extend(
        physical_labels
    )

    combined.extend(
        behavior_labels
    )


    combined = list(
        dict.fromkeys(
            combined
        )
    )


    if combined:

        config.last_detected_object = (
            ", ".join(
                combined
            )
        )

    else:

        config.last_detected_object = "NONE"


# ============================================================
# BOX COLOR
# ============================================================

def get_box_color(label):

    name = normalize_label(
        label
    )


    if name in {

        "phone",
        "book",
        "paper",

        "calculator",
        "earphone",
        "sunglasses",
        "watch",

        "cheating",
        "cheat_paper",
        "look_around",
        "use_phone",

    }:

        return (
            0,
            0,
            255
        )


    if name == "normal":

        return (
            0,
            255,
            0
        )


    if name == "face":

        return (
            255,
            0,
            0
        )


    if name in {

        "fist",
        "index_left",
        "index_right",
        "open_palm",
        "point",
        "thumbs_down",
        "thumbs_up",

    }:

        return (
            255,
            255,
            0
        )


    return (
        0,
        255,
        255
    )


# ============================================================
# DRAW DETECTION
# ============================================================

def draw_detection(
    frame,
    detection
):

    try:

        label = detection["label"]

        confidence = float(
            detection["confidence"]
        )

        x1, y1, x2, y2 = (
            detection["box"]
        )

    except Exception:

        return


    color = get_box_color(
        label
    )


    cv2.rectangle(

        frame,

        (x1, y1),

        (x2, y2),

        color,

        2

    )


    text = (
        f"{label} "
        f"{confidence:.2f}"
    )


    text_y = max(
        y1 - 8,
        20
    )


    (
        text_width,
        text_height
    ), _ = cv2.getTextSize(

        text,

        cv2.FONT_HERSHEY_SIMPLEX,

        0.50,

        1

    )


    cv2.rectangle(

        frame,

        (
            x1,
            text_y
            - text_height
            - 5
        ),

        (
            x1
            + text_width
            + 5,
            text_y
            + 2
        ),

        color,

        -1

    )


    cv2.putText(

        frame,

        text,

        (
            x1 + 2,
            text_y - 2
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.50,

        (
            255,
            255,
            255
        ),

        1,

        cv2.LINE_AA

    )


# ============================================================
# UPDATE FPS
# ============================================================

def update_fps():

    global _fps
    global _fps_counter
    global _fps_start_time


    _fps_counter += 1


    elapsed = (
        time.time()
        - _fps_start_time
    )


    if elapsed >= 1.0:

        _fps = (
            _fps_counter
            / elapsed
        )

        _fps_counter = 0

        _fps_start_time = time.time()


    return _fps


# ============================================================
# UPDATE DASHBOARD
# ============================================================

def update_dashboard():

    try:

        config.dashboard.update({

            "face_count":
                config.face_count,

            "face_status":
                config.face_status,

            "face_verified":
                getattr(
                    config,
                    "face_verified",
                    False
                ),

            "gaze":
                getattr(
                    config,
                    "gaze_direction",
                    "CENTER"
                ),

            "head":
                getattr(
                    config,
                    "head_direction",
                    "FORWARD"
                ),

            "paper":
                config.paper_detected,

            "phone":
                config.phone_detected,

            "book":
                config.book_detected,

            "calculator":
                config.calculator_detected,

            "earphone":
                config.earphone_detected,

            "sunglasses":
                config.sunglasses_detected,

            "watch":
                config.watch_detected,

            "object":
                getattr(
                    config,
                    "last_detected_object",
                    "NONE"
                ),

            "objects":
                list(
                    getattr(
                        config,
                        "detected_objects",
                        []
                    )
                ),

            "restricted_objects":
                list(
                    getattr(
                        config,
                        "detected_restricted_objects",
                        []
                    )
                ),

            "behavior":
                getattr(
                    config,
                    "behavior_status",
                    "NORMAL"
                ),

            "behavior_score":
                getattr(
                    config,
                    "behavior_score",
                    0
                ),

            "behavior_reasons":
                list(
                    getattr(
                        config,
                        "behavior_reasons",
                        []
                    )
                ),

            "violations":
                config.total_violations,

            "exam":
                getattr(
                    config,
                    "exam_name",
                    ""
                ),

            "status":
                (
                    "RUNNING"
                    if config.exam_started
                    else "NOT STARTED"
                ),

            "student_id":
                getattr(
                    config,
                    "student_id",
                    ""
                ),

            "student_name":
                getattr(
                    config,
                    "student_name",
                    ""
                ),

        })

    except Exception as e:

        print(
            "Dashboard update error:",
            e
        )


# ============================================================
# DRAW SYSTEM OVERLAY
# ============================================================

def draw_overlay(
    annotated_frame,
    detected_objects,
    fps
):

    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    objects_text = (

        ", ".join(
            detected_objects
        )

        if detected_objects

        else "NONE"

    )


    cv2.putText(

        annotated_frame,

        f"Objects: {objects_text}",

        (15, 30),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (
            255,
            255,
            255
        ),

        2,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # Physical flags
    # --------------------------------------------------------

    flags_text = (

        f"Phone:{config.phone_detected} "
        f"Book:{config.book_detected} "
        f"Paper:{config.paper_detected} "
        f"Calc:{config.calculator_detected}"

    )


    cv2.putText(

        annotated_frame,

        flags_text,

        (15, 56),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.45,

        (
            255,
            255,
            255
        ),

        1,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # Additional object flags
    # --------------------------------------------------------

    flags_text_2 = (

        f"Ear:{config.earphone_detected} "
        f"Glass:{config.sunglasses_detected} "
        f"Watch:{config.watch_detected}"

    )


    cv2.putText(

        annotated_frame,

        flags_text_2,

        (15, 78),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.45,

        (
            255,
            255,
            255
        ),

        1,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # Violations
    # --------------------------------------------------------

    cv2.putText(

        annotated_frame,

        (
            f"Violations: "
            f"{config.total_violations}"
        ),

        (15, 104),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.60,

        (
            0,
            0,
            255
        ),

        2,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # Behavior
    # --------------------------------------------------------

    behavior = getattr(

        config,

        "behavior_status",

        "NORMAL"

    )


    cv2.putText(

        annotated_frame,

        f"Behavior: {behavior}",

        (15, 130),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        (
            0,
            255,
            255
        ),

        2,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # Face
    # --------------------------------------------------------

    cv2.putText(

        annotated_frame,

        (
            f"Face: "
            f"{config.face_count} "
            f"({config.face_status})"
        ),

        (15, 156),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.48,

        (
            255,
            255,
            255
        ),

        1,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status = getattr(

        config,

        "current_status",

        ""

    )


    if not status:

        status = (

            "RUNNING"

            if config.exam_started

            else "NOT STARTED"

        )


    cv2.putText(

        annotated_frame,

        f"Status: {status}",

        (15, 182),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.50,

        (
            255,
            255,
            255
        ),

        1,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # Performance
    # --------------------------------------------------------

    cv2.putText(

        annotated_frame,

        (
            f"FPS: {fps:.1f} "
            f"AI: {_last_inference_ms:.0f}ms"
        ),

        (15, 208),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.45,

        (
            200,
            200,
            200
        ),

        1,

        cv2.LINE_AA

    )


# ============================================================
# MAIN DETECT FUNCTION
# ============================================================

def detect(frame):

    global _frame_counter
    global _last_results
    global _last_detection_time
    global _last_inference_frame


    if frame is None:

        return frame, []


    _frame_counter += 1


    annotated_frame = frame.copy()


    # ========================================================
    # RUN AI ONLY EVERY N FRAMES
    # ========================================================

    should_detect = (

        _frame_counter
        % DETECTION_INTERVAL
        == 0

    )


    fresh_inference = False


    # ========================================================
    # FRESH AI INFERENCE
    # ========================================================

    if should_detect:

        detections = run_all_models(
            frame
        )


        # ----------------------------------------------------
        # Remove duplicates within same model.
        # ----------------------------------------------------

        detections = (
            remove_duplicate_detections(
                detections
            )
        )


        detections = (
            keep_best_per_model_label(
                detections
            )
        )


        _last_results = detections

        _last_detection_time = (
            time.time()
        )

        _last_inference_frame = (
            _frame_counter
        )

        fresh_inference = True


    else:

        detections = _last_results


    # ========================================================
    # STALE RESULTS
    # ========================================================

    if (

        time.time()
        - _last_detection_time
        > DETECTION_TIMEOUT

    ):

        detections = []

        _last_results = []


    # ========================================================
    # RESET LIVE FLAGS
    # ========================================================

    reset_live_flags()


    # ========================================================
    # UPDATE PHYSICAL FLAGS
    #
    # Behavior does NOT modify physical flags.
    # ========================================================

    update_physical_flags(
        detections
    )


    # ========================================================
    # TEMPORAL VIOLATION PROCESSING
    #
    # ONLY fresh AI inference participates.
    # ========================================================

    if fresh_inference:

        inference_number = (
            _last_inference_frame
        )


        process_confirmed_violations(

            detections,

            frame,

            inference_number

        )


    # ========================================================
    # LAST DETECTED OBJECT
    # ========================================================

    update_last_detected_object(
        detections
    )


    # ========================================================
    # DETECTED OBJECT LIST
    # ========================================================

    detected_objects = []


    for detection in detections:

        label = detection.get(
            "label",
            ""
        )


        if not label:

            continue


        detected_objects.append(
            label
        )


        draw_detection(

            annotated_frame,

            detection

        )


    detected_objects = list(

        dict.fromkeys(
            detected_objects
        )

    )


    # ========================================================
    # CURRENT STATUS
    #
    # A confirmed violation is shown as VIOLATION for the
    # current alert period. It is not generated by cached
    # detections.
    # ========================================================

    if not config.exam_started:

        config.current_status = (
            "NOT STARTED"
        )

    else:

        last_violation_time = float(
            getattr(
                config,
                "last_violation_time",
                0
            )
        )


        if (

            last_violation_time > 0

            and

            (
                time.time()
                - last_violation_time
            )
            < VIOLATION_COOLDOWN

        ):

            config.current_status = (
                "VIOLATION"
            )

        else:

            config.current_status = (
                "RUNNING"
            )


    # ========================================================
    # DASHBOARD
    # ========================================================

    update_dashboard()


    # ========================================================
    # FPS
    # ========================================================

    fps = update_fps()


    # ========================================================
    # OVERLAY
    # ========================================================

    draw_overlay(

        annotated_frame,

        detected_objects,

        fps

    )


    # ========================================================
    # RETURN
    # ========================================================

    return (
        annotated_frame,
        detected_objects
    )


# ============================================================
# RESET DETECTOR STATE
# ============================================================

def reset_detector_state():

    global _frame_counter
    global _last_results
    global _last_detection_time
    global _last_inference_frame

    global _last_violation_time

    global _behavior_candidate
    global _behavior_candidate_count
    global _behavior_last_seen_inference

    global _object_candidate_counts
    global _object_last_seen_inference

    global _fps
    global _fps_counter
    global _fps_start_time
    global _last_inference_ms


    _frame_counter = 0

    _last_results = []

    _last_detection_time = 0.0

    _last_inference_frame = 0


    _last_violation_time = {}


    # --------------------------------------------------------
    # Behavior
    # --------------------------------------------------------

    _behavior_candidate = ""

    _behavior_candidate_count = 0

    _behavior_last_seen_inference = 0


    # --------------------------------------------------------
    # Objects
    # --------------------------------------------------------

    _object_candidate_counts = {}

    _object_last_seen_inference = {}


    # --------------------------------------------------------
    # FPS
    # --------------------------------------------------------

    _fps = 0.0

    _fps_counter = 0

    _fps_start_time = time.time()

    _last_inference_ms = 0.0


    # --------------------------------------------------------
    # Config state
    # --------------------------------------------------------

    try:

        config.reset_detection_state()

    except Exception as e:

        print(
            "Config reset error:",
            e
        )


    print(
        "Detector state reset."
    )


# ============================================================
# MODEL STATUS
# ============================================================

def get_model_status():

    return {

        name:
            model is not None

        for name, model
        in models.items()

    }


# ============================================================
# PERFORMANCE STATUS
# ============================================================

def get_performance_status():

    return {

        "device":
            DEVICE_NAME,

        "fps":
            round(
                _fps,
                2
            ),

        "inference_ms":
            round(
                _last_inference_ms,
                2
            ),

        "detection_interval":
            DETECTION_INTERVAL,

        "inference_size":
            INFERENCE_SIZE,

        "book_phone_confidence":
            BOOK_PHONE_CONFIDENCE,

        "behavior_confidence":
            BEHAVIOR_CONFIDENCE,

        "face_hand_confidence":
            FACE_HAND_CONFIDENCE,

        "object_confidence":
            OBJECT_CONFIDENCE,

        "object_confirmation":
            OBJECT_CONFIRM_FRAMES,

        "behavior_confirmation":
            BEHAVIOR_CONFIRM_FRAMES,

        "violation_cooldown":
            VIOLATION_COOLDOWN,

        "detection_timeout":
            DETECTION_TIMEOUT,

    }


# ============================================================
# CONFIRMATION STATUS
# ============================================================

def get_confirmation_status():

    return {

        "objects":
            dict(
                _object_candidate_counts
            ),

        "behavior": {

            "candidate":
                _behavior_candidate,

            "count":
                _behavior_candidate_count,

            "required":
                BEHAVIOR_CONFIRM_FRAMES,

        },

    }


# ============================================================
# LIVE DETECTION STATE
# ============================================================

def get_detection_state():

    return {

        "phone":
            bool(
                config.phone_detected
            ),

        "book":
            bool(
                config.book_detected
            ),

        "paper":
            bool(
                config.paper_detected
            ),

        "calculator":
            bool(
                config.calculator_detected
            ),

        "earphone":
            bool(
                config.earphone_detected
            ),

        "sunglasses":
            bool(
                config.sunglasses_detected
            ),

        "watch":
            bool(
                config.watch_detected
            ),

        "objects":
            list(
                getattr(
                    config,
                    "detected_objects",
                    []
                )
            ),

        "restricted_objects":
            list(
                getattr(
                    config,
                    "detected_restricted_objects",
                    []
                )
            ),

        "face_count":
            int(
                config.face_count
            ),

        "face_status":
            config.face_status,

        "behavior":
            config.behavior_status,

        "behavior_score":
            config.behavior_score,

        "violations":
            config.total_violations,

        "status":
            config.current_status,

        "last_object":
            config.last_detected_object,

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("DETECTOR TEST")
    print("=" * 70)

    print(
        "Loaded models:",
        list(
            models.keys()
        )
    )

    print(
        "Model status:",
        get_model_status()
    )

    print(
        "Device:",
        DEVICE_NAME
    )

    print(
        "Inference size:",
        INFERENCE_SIZE
    )

    print(
        "Detection interval:",
        DETECTION_INTERVAL
    )

    print(
        "Book/Phone confidence:",
        BOOK_PHONE_CONFIDENCE
    )

    print(
        "Behavior confidence:",
        BEHAVIOR_CONFIDENCE
    )

    print(
        "Face/Hand confidence:",
        FACE_HAND_CONFIDENCE
    )

    print(
        "Object confidence:",
        OBJECT_CONFIDENCE
    )

    print(
        "Object confirmation:",
        OBJECT_CONFIRM_FRAMES
    )

    print(
        "Behavior confirmation:",
        BEHAVIOR_CONFIRM_FRAMES
    )

    print(
        "Detection timeout:",
        DETECTION_TIMEOUT
    )

    print(
        "Violation cooldown:",
        VIOLATION_COOLDOWN
    )

    print()
    print("Detection state:")
    print(
        get_detection_state()
    )

    print()
    print("DETECTOR OK")
    print("=" * 70)

