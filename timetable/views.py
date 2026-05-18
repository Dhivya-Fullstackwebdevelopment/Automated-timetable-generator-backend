import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from subject.models import Subject
from staff.models import Staff
from django.contrib.auth.models import User

ROOMS = ["Room 101", "Room 102", "Room 201", "Room 202", "Lab 1", "Lab 2"]


@api_view(['POST'])
def admin_login(request):

    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({
            "status": False,
            "message": "Email and password required"
        })

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            "status": False,
            "message": "Invalid login credentials"
        })

    if not user.check_password(password):
        return Response({
            "status": False,
            "message": "Invalid login credentials"
        })

    if not user.is_staff:
        return Response({
            "status": False,
            "message": "You are not an admin"
        })

    return Response({
        "status": True,
        "message": "Admin login successful",
        "data": {
            "email": user.email,
            "username": user.username
        }
    })


@api_view(['POST'])
def generate_timetable(request):

    type_value = request.data.get("type")
    department = request.data.get("department")
    year = request.data.get("year")
    semester = request.data.get("semester")

    if str(type_value) == "1":
        if not department:
            return Response({
                "status": False,
                "message": "department required for type 1"
            })
        subject_filter = {"department": department}
    else:
        if not department or not year or not semester:
            return Response({
                "status": False,
                "message": "department, year, semester required"
            })
        subject_filter = {
            "department": department,
            "year": year,
            "semester": semester
        }

    subjects = list(Subject.objects.filter(**subject_filter).order_by('id'))
    all_staff = list(Staff.objects.filter(department=department).order_by('id'))

    if not subjects:
        return Response({"status": False, "message": "No subjects found"})

    if not all_staff:
        return Response({"status": False, "message": "No staff found"})

    subject_staff_map = {}

    for sub in subjects:

        # Staff who can teach this subject AND are ACTIVE
        active_staff = [
            s for s in all_staff
            if sub.name.lower() in (s.subjects or "").lower()
            and s.status == "ACTIVE"
        ]

        # Staff who can teach this subject BUT are NOT ACTIVE (on leave etc.)
        inactive_staff = [
            s for s in all_staff
            if sub.name.lower() in (s.subjects or "").lower()
            and s.status != "ACTIVE"
        ]

        # Any other staff who can substitute (not subject-specific)
        substitute_staff = [
            s for s in all_staff
            if s.status == "ACTIVE"
            and sub.name.lower() not in (s.subjects or "").lower()
        ]

        if active_staff:
            # ✅ Normal case — assign active subject teacher
            subject_staff_map[sub.name] = {
                "type": "active",
                "staff": active_staff,
                "substitute": None
            }
        elif inactive_staff:
            # ⚠️ Subject teacher exists but NOT ACTIVE
            # → assign a substitute from active staff
            if substitute_staff:
                subject_staff_map[sub.name] = {
                    "type": "substituted",
                    "original_staff": inactive_staff,
                    "staff": substitute_staff,  # substitute takes the class
                    "substitute": substitute_staff
                }
            else:
                # No active substitute available, use inactive as fallback
                subject_staff_map[sub.name] = {
                    "type": "substituted",
                    "original_staff": inactive_staff,
                    "staff": inactive_staff,
                    "substitute": inactive_staff
                }
        else:
            # No staff found for this subject at all → use any active staff
            fallback = [s for s in all_staff if s.status == "ACTIVE"] or all_staff
            subject_staff_map[sub.name] = {
                "type": "substituted",
                "staff": fallback,
                "substitute": fallback
            }

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    periods = 8
    timetable = []
    used_slots = {}
    subject_keys = list(subject_staff_map.keys())

    for d_index, day in enumerate(days):
        row = []

        rng = random.Random(d_index + 42)
        day_subjects = subject_keys.copy()
        rng.shuffle(day_subjects)

        for p in range(periods):
            sub = day_subjects[p % len(day_subjects)]
            info = subject_staff_map[sub]
            staff_choices = info["staff"]
            staff_type = info["type"]
            staff = staff_choices[(d_index + p) % len(staff_choices)]
            key = f"{staff.id}-{day}-{p}"

            if key in used_slots:
                row.append({
                    "subject": "Free",
                    "staff": "",
                    "room": "",
                    "year": f"{year} Year",
                    "status": "free",
                    "substitute": None,
                    "staff_status": None
                })
            else:
                used_slots[key] = True

                # If substituted, show original staff name in substitute field
                original = info.get("original_staff")
                substitute_name = None
                if staff_type == "substituted":
                    substitute_name = staff.name  # who is actually taking the class
                    original_name = original[0].name if original else None
                else:
                    original_name = None

                row.append({
                    "subject": sub,
                    "staff": staff.name,           # who is actually in class
                    "room": ROOMS[(d_index + p) % len(ROOMS)],
                    "year": f"{year} Year",
                    "status": staff_type,          # "active" or "substituted"
                    "original_staff": original_name,   # original teacher (if on leave)
                    "substitute": substitute_name,     # substitute teacher name
                    "staff_status": staff.status
                })

        timetable.append({"day": day, "periods": row})

    return Response({
        "status": True,
        "message": "Timetable generated successfully",
        "data": timetable
    })