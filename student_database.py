# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# VIRTUAL STUDENT DATABASE
# ============================================================

STUDENTS = {

    1: {
        "id": "22KD1A0501",
        "name": "Balaji",
        "branch": "CSE"
    },

    2: {
        "id": "22KD1A0502",
        "name": "Rahul",
        "branch": "CSE"
    },

    3: {
        "id": "22KD1A0503",
        "name": "Sai",
        "branch": "CSE"
    },

    4: {
        "id": "22KD1A0504",
        "name": "Kiran",
        "branch": "CSE"
    },

    5: {
        "id": "22KD1A0505",
        "name": "Ravi",
        "branch": "CSE"
    }

}


# ============================================================
# GET STUDENT
# ============================================================

def get_student(student_number):

    return STUDENTS.get(student_number)


# ============================================================
# GET ALL STUDENTS
# ============================================================

def get_all_students():

    return list(STUDENTS.values())


# ============================================================
# STUDENT COUNT
# ============================================================

def get_student_count():

    return len(STUDENTS)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("VIRTUAL STUDENT DATABASE TEST")
    print("=" * 60)

    print("Total students:", get_student_count())

    print()

    for number, student in STUDENTS.items():

        print(
            number,
            "->",
            student["id"],
            "|",
            student["name"],
            "|",
            student["branch"]
        )

    print("=" * 60)