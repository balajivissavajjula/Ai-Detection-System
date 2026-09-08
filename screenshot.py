
# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# ROBUST VIOLATION SCREENSHOT MODULE
# ============================================================

import cv2

from datetime import datetime

from pathlib import Path

import config


# ============================================================
# MODULE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_SCREENSHOT_DIR = (
    BASE_DIR / "screenshots"
)


# ============================================================
# SAFE FILENAME
# ============================================================

def make_safe_filename(value):

    value = str(value).strip()

    if not value:
        value = "violation"

    safe = ""

    for character in value:

        if (
            character.isalnum()
            or character in ("_", "-")
        ):
            safe += character

        else:
            safe += "_"

    safe = safe[:80]

    return safe or "violation"


# ============================================================
# GET SCREENSHOT DIRECTORY
# ============================================================

def get_screenshot_directory():

    configured_directory = getattr(
        config,
        "SCREENSHOT_DIR",
        None
    )

    if configured_directory:

        try:
            directory = Path(
                configured_directory
            )

            if not directory.is_absolute():

                directory = (
                    BASE_DIR / directory
                )

        except Exception:

            directory = (
                DEFAULT_SCREENSHOT_DIR
            )

    else:

        directory = (
            DEFAULT_SCREENSHOT_DIR
        )


    try:

        directory.mkdir(
            parents=True,
            exist_ok=True
        )

    except Exception as e:

        print()
        print("=" * 70)
        print("SCREENSHOT DIRECTORY ERROR")
        print("=" * 70)

        print(
            "Directory:",
            directory
        )

        print(
            "Error:",
            repr(e)
        )

        print("=" * 70)

        return None


    return directory


# ============================================================
# CREATE UNIQUE PATH
# ============================================================

def create_screenshot_path(
    directory,
    label,
    extension="jpg"
):

    safe_label = make_safe_filename(
        label
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filename = (
        f"{safe_label}_"
        f"{timestamp}."
        f"{extension}"
    )

    return directory / filename


# ============================================================
# VALIDATE FRAME
# ============================================================

def validate_frame(frame):

    if frame is None:

        print(
            "SCREENSHOT ERROR: frame is None"
        )

        return False


    if not hasattr(
        frame,
        "shape"
    ):

        print(
            "SCREENSHOT ERROR: invalid frame"
        )

        return False


    if len(frame.shape) < 2:

        print(
            "SCREENSHOT ERROR: frame has invalid shape:",
            frame.shape
        )

        return False


    height = frame.shape[0]

    width = frame.shape[1]


    if height <= 0 or width <= 0:

        print(
            "SCREENSHOT ERROR: empty frame:",
            frame.shape
        )

        return False


    return True


# ============================================================
# SAVE JPEG
# ============================================================

def save_jpeg(
    frame,
    filepath
):

    try:

        success = cv2.imwrite(
            str(filepath),
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                95
            ]
        )

    except Exception as e:

        print(
            "JPEG write exception:",
            repr(e)
        )

        return False


    if not success:

        print(
            "JPEG write FAILED:",
            filepath
        )

        return False


    try:

        if not filepath.exists():

            print(
                "JPEG reported success but file does not exist:",
                filepath
            )

            return False


        if filepath.stat().st_size <= 0:

            print(
                "JPEG file is empty:",
                filepath
            )

            return False

    except Exception as e:

        print(
            "JPEG verification error:",
            repr(e)
        )

        return False


    return True


# ============================================================
# SAVE PNG FALLBACK
# ============================================================

def save_png(
    frame,
    filepath
):

    try:

        success = cv2.imwrite(
            str(filepath),
            frame
        )

    except Exception as e:

        print(
            "PNG write exception:",
            repr(e)
        )

        return False


    if not success:

        print(
            "PNG write FAILED:",
            filepath
        )

        return False


    try:

        if not filepath.exists():

            return False


        if filepath.stat().st_size <= 0:

            return False

    except Exception:

        return False


    return True


# ============================================================
# SAVE VIOLATION SCREENSHOT
# ============================================================

def save_screenshot(
    frame,
    label
):

    """
    Save confirmed violation screenshot.

    Returns:
        True  -> successfully saved
        False -> failed / disabled
    """

    print()
    print(
        "SCREENSHOT REQUEST |",
        label
    )


    # --------------------------------------------------------
    # Frame check
    # --------------------------------------------------------

    if not validate_frame(frame):

        return False


    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    enabled = getattr(
        config,
        "SAVE_VIOLATION_SCREENSHOTS",
        True
    )


    if not enabled:

        print(
            "SCREENSHOT DISABLED:"
            " SAVE_VIOLATION_SCREENSHOTS=False"
        )

        return False


    # --------------------------------------------------------
    # Directory
    # --------------------------------------------------------

    directory = (
        get_screenshot_directory()
    )


    if directory is None:

        return False


    # --------------------------------------------------------
    # Print useful diagnostic information
    # --------------------------------------------------------

    print(
        "Screenshot directory:",
        directory
    )

    print(
        "Frame shape:",
        frame.shape
    )

    print(
        "Frame dtype:",
        frame.dtype
    )


    # --------------------------------------------------------
    # Try JPEG
    # --------------------------------------------------------

    jpeg_path = create_screenshot_path(
        directory,
        label,
        "jpg"
    )


    if save_jpeg(
        frame,
        jpeg_path
    ):

        print()
        print(
            "=" * 70
        )

        print(
            "VIOLATION SCREENSHOT SAVED"
        )

        print(
            "Label:",
            label
        )

        print(
            "File:",
            jpeg_path
        )

        print(
            "Size:",
            jpeg_path.stat().st_size,
            "bytes"
        )

        print(
            "=" * 70
        )

        return True


    # --------------------------------------------------------
    # JPEG failed -> PNG fallback
    # --------------------------------------------------------

    print(
        "JPEG failed."
        " Trying PNG fallback..."
    )


    png_path = create_screenshot_path(
        directory,
        label,
        "png"
    )


    if save_png(
        frame,
        png_path
    ):

        print()
        print(
            "=" * 70
        )

        print(
            "VIOLATION SCREENSHOT SAVED"
        )

        print(
            "Format: PNG fallback"
        )

        print(
            "Label:",
            label
        )

        print(
            "File:",
            png_path
        )

        print(
            "Size:",
            png_path.stat().st_size,
            "bytes"
        )

        print(
            "=" * 70
        )

        return True


    # --------------------------------------------------------
    # Complete failure
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "SCREENSHOT SAVE FAILED"
    )

    print(
        "Label:",
        label
    )

    print(
        "Directory:",
        directory
    )

    print(
        "JPEG:",
        jpeg_path
    )

    print(
        "PNG:",
        png_path
    )

    print(
        "Check folder permissions."
    )

    print(
        "=" * 70
    )


    return False


# ============================================================
# SAVE NORMAL SCREENSHOT
# ============================================================

def save_normal_screenshot(
    frame,
    prefix="frame"
):

    if not validate_frame(frame):

        return False


    enabled = getattr(
        config,
        "SAVE_SCREENSHOTS",
        True
    )


    if not enabled:

        print(
            "Normal screenshot disabled."
        )

        return False


    directory = (
        get_screenshot_directory()
    )


    if directory is None:

        return False


    filepath = create_screenshot_path(
        directory,
        prefix,
        "jpg"
    )


    if save_jpeg(
        frame,
        filepath
    ):

        print(
            "Normal screenshot saved:",
            filepath
        )

        return True


    return False


# ============================================================
# GET SCREENSHOT FILES
# ============================================================

def get_screenshot_files():

    directory = (
        get_screenshot_directory()
    )


    if directory is None:

        return []


    try:

        files = []

        files.extend(
            directory.glob("*.jpg")
        )

        files.extend(
            directory.glob("*.jpeg")
        )

        files.extend(
            directory.glob("*.png")
        )


        files.sort(
            key=lambda file:
                file.stat().st_mtime,
            reverse=True
        )


        return files

    except Exception as e:

        print(
            "Screenshot listing error:",
            repr(e)
        )

        return []


# ============================================================
# SCREENSHOT COUNT
# ============================================================

def get_screenshot_count():

    return len(
        get_screenshot_files()
    )


# ============================================================
# TEST SCREENSHOT DIRECTLY
# ============================================================

def test_screenshot():

    print()
    print(
        "=" * 70
    )

    print(
        "SCREENSHOT WRITE TEST"
    )

    print(
        "=" * 70
    )


    directory = (
        get_screenshot_directory()
    )


    print(
        "Directory:",
        directory
    )


    print(
        "Violation screenshots:",
        getattr(
            config,
            "SAVE_VIOLATION_SCREENSHOTS",
            True
        )
    )


    print(
        "Normal screenshots:",
        getattr(
            config,
            "SAVE_SCREENSHOTS",
            True
        )
    )


    if directory is not None:

        print(
            "Directory exists:",
            directory.exists()
        )

        print(
            "Directory writable test..."
        )

        try:

            test_file = (
                directory
                / "_write_test.txt"
            )

            test_file.write_text(
                "screenshot module test",
                encoding="utf-8"
            )

            print(
                "Write test: OK"
            )

            test_file.unlink(
                missing_ok=True
            )

        except Exception as e:

            print(
                "Write test: FAILED"
            )

            print(
                "Error:",
                repr(e)
            )


    print(
        "Existing screenshots:",
        get_screenshot_count()
    )


    print(
        "=" * 70
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    test_screenshot()
