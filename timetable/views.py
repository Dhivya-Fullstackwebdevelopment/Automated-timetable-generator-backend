import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from subject.models import Subject
from staff.models import Staff
from django.contrib.auth.models import User  # ← CHANGE THIS IMPORT


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

    # Get user from auth_user table by email
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            "status": False,
            "message": "Invalid login credentials"
        })

    # Check password
    if not user.check_password(password):
        return Response({
            "status": False,
            "message": "Invalid login credentials"
        })

    # Check is_staff = 1
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
        active_staff = [
            s for s in all_staff
            if sub.name.lower() in (s.subjects or "").lower()
            and s.status == "ACTIVE"
        ]
        non_active_staff = [
            s for s in all_staff
            if sub.name.lower() in (s.subjects or "").lower()
            and s.status != "ACTIVE"
        ]

        if active_staff:
            subject_staff_map[sub.name] = {"type": "active", "staff": active_staff}
        elif non_active_staff:
            subject_staff_map[sub.name] = {"type": "substituted", "staff": non_active_staff}
        else:
            subject_staff_map[sub.name] = {"type": "substituted", "staff": all_staff}

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
                    "subject": "Free", "staff": "", "room": "",
                    "year": f"{year} Year", "status": "free",
                    "substitute": None, "staff_status": None
                })
            else:
                used_slots[key] = True
                row.append({
                    "subject": sub,
                    "staff": staff.name,
                    "room": ROOMS[(d_index + p) % len(ROOMS)],
                    "year": f"{year} Year",
                    "status": staff_type,
                    "substitute": None if staff_type == "active" else staff.name,
                    "staff_status": staff.status
                })

        timetable.append({"day": day, "periods": row})

    return Response({
        "status": True,
        "message": "Timetable generated successfully",
        "data": timetable
    })