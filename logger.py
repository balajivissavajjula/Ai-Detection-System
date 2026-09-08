# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# VIOLATION LOGGER
# ============================================================

import csv
from datetime import datetime

import config


# ============================================================
# LOG FILE
# ============================================================

VIOLATION_LOG_FILE = (
    config.LOG_DIR / "violations.csv"
)


# ============================================================
# ENSURE LOG DIRECTORY
# ============================================================

def ensure_log_directory():
    """
    Make sure the logs directory exists.
    """

    try:

        config.LOG_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        return True

    except Exception as e:

        print(
            "Log directory error:",
            e
        )

        return False


# ============================================================
# LOG VIOLATION
# ============================================================

def log_violation(label, status):
    """
    Save a violation into violations.csv.

    Parameters
    ----------
    label : str
        Violation/object/behavior label.

    status : str
        Current status or reason.

    Returns
    -------
    bool
        True if logging succeeded.
    """

    # --------------------------------------------------------
    # Make sure log directory exists
    # --------------------------------------------------------

    if not ensure_log_directory():

        return False

    # --------------------------------------------------------
    # Clean values
    # --------------------------------------------------------

    label = str(
        label if label is not None else "UNKNOWN"
    ).strip()

    status = str(
        status if status is not None else ""
    ).strip()

    exam_name = str(
        getattr(
            config,
            "exam_name",
            ""
        )
    ).strip()

    if not label:

        label = "UNKNOWN"

    if not status:

        status = "VIOLATION"

    # --------------------------------------------------------
    # Check whether file already exists
    # --------------------------------------------------------

    file_exists = (
        VIOLATION_LOG_FILE.exists()
        and VIOLATION_LOG_FILE.stat().st_size > 0
    )

    # --------------------------------------------------------
    # Current timestamp
    # --------------------------------------------------------

    now = datetime.now()

    # --------------------------------------------------------
    # Write CSV
    # --------------------------------------------------------

    try:

        with open(
            VIOLATION_LOG_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            # ------------------------------------------------
            # Header
            # ------------------------------------------------

            if not file_exists:

                writer.writerow([
                    "Date",
                    "Time",
                    "Exam",
                    "Violation",
                    "Status"
                ])

            # ------------------------------------------------
            # Violation record
            # ------------------------------------------------

            writer.writerow([

                now.strftime(
                    "%d-%m-%Y"
                ),

                now.strftime(
                    "%H:%M:%S"
                ),

                exam_name,

                label,

                status

            ])

        print(
            "Violation logged:",
            label,
            "|",
            status
        )

        return True

    except Exception as e:

        print(
            "Violation log error:",
            e
        )

        return False


# ============================================================
# READ VIOLATION LOGS
# ============================================================

def get_violation_logs():
    """
    Read all violation records from CSV.

    Returns
    -------
    list
        List of violation dictionaries.
    """

    if not VIOLATION_LOG_FILE.exists():

        return []

    records = []

    try:

        with open(
            VIOLATION_LOG_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                records.append({
                    "date":
                        row.get(
                            "Date",
                            ""
                        ),

                    "time":
                        row.get(
                            "Time",
                            ""
                        ),

                    "exam":
                        row.get(
                            "Exam",
                            ""
                        ),

                    "violation":
                        row.get(
                            "Violation",
                            ""
                        ),

                    "status":
                        row.get(
                            "Status",
                            ""
                        )
                })

        return records

    except Exception as e:

        print(
            "Violation log read error:",
            e
        )

        return []


# ============================================================
# GET RECENT VIOLATIONS
# ============================================================

def get_recent_violations(limit=20):
    """
    Return the latest violation records.
    """

    try:

        limit = max(
            1,
            int(limit)
        )

    except Exception:

        limit = 20

    records = get_violation_logs()

    return records[-limit:]


# ============================================================
# CLEAR VIOLATION LOG
# ============================================================

def clear_violation_logs():
    """
    Clear the complete violations CSV.

    Returns
    -------
    bool
        True if successful.
    """

    try:

        if VIOLATION_LOG_FILE.exists():

            VIOLATION_LOG_FILE.unlink()

        print(
            "Violation logs cleared."
        )

        return True

    except Exception as e:

        print(
            "Violation log clear error:",
            e
        )

        return False


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("VIOLATION LOGGER TEST")
    print("=" * 60)

    print(
        "Log file:",
        VIOLATION_LOG_FILE
    )

    print()

    if log_violation(
        "TEST_VIOLATION",
        "TEST"
    ):

        print(
            "Logger test successful."
        )

    else:

        print(
            "Logger test FAILED."
        )

    print()

    logs = get_recent_violations(5)

    print(
        "Recent records:"
    )

    for record in logs:

        print(
            record
        )

    print()
    print("=" * 60)