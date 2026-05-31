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

    if email == "admin@gmail.com" and password == "admin@123":
        return Response({
            "status": True,
            "message": "Admin login successful"
        })

    return Response({
        "status": False,
        "message": "Invalid login credentials"
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

@api_view(['GET'])
def dashboard(request):

    from department.models import Department
    from staff.models import Staff
    from subject.models import Subject

    # Department counts
    all_departments = Department.objects.all()
    total_departments = all_departments.count()

    # Print to see what 'type' values look like — check terminal
    for d in all_departments:
        print(f"Department: {d.name}, type: {d.type}")

    # Staff counts
    all_staff = Staff.objects.all()
    active_staff = all_staff.filter(status="ACTIVE").count()
    on_leave_staff = all_staff.filter(status="ON_LEAVE").count()
    resigned_staff = all_staff.filter(status="RESIGNED").count()

    # Subject counts
    all_subjects = Subject.objects.all()
    total_subjects = all_subjects.count()
    lab_subjects = all_subjects.filter(name__icontains="lab").count()

    # Build department list without filtering by type
    department_list = list(all_departments.values("id", "name", "type"))

    return Response({
        "status": True,
        "message": "Dashboard data fetched successfully",
        "data": {
            "departments": {
                "total": total_departments,
                "list": department_list
            },
            "staff": {
                "active": active_staff,
                "on_leave": on_leave_staff,
                "resigned": resigned_staff
            },
            "subjects": {
                "total": total_subjects,
                "lab_subjects": lab_subjects
            },
            "timetables": {
                "total": 0
            }
        }
    })

    # In timetable/views.py - add these two new APIs

@api_view(['POST'])
def staff_login(request):
    from staff.models import Staff

    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({
            "status": False,
            "message": "Email and password required"
        })

    try:
        staff = Staff.objects.select_related('department').get(email=email)
    except Staff.DoesNotExist:
        return Response({
            "status": False,
            "message": "Invalid login credentials"
        })

    if staff.password != password:
        return Response({
            "status": False,
            "message": "Invalid login credentials"
        })

    return Response({
        "status": True,
        "message": "Staff login successful",
        "data": {
            "id": staff.id,
            "name": staff.name,
            "email": staff.email,
            "department": staff.department.name if staff.department else "",
            "department_type": staff.department.type if staff.department else "",
            "subjects": staff.subjects,
            "status": staff.status,
            "joined": str(staff.created_at) if hasattr(staff, 'created_at') else ""
        }
    })


@api_view(['GET'])
def staff_dashboard(request, staff_id):
    from staff.models import Staff
    import datetime

    try:
        staff = Staff.objects.select_related('department').get(id=staff_id)
    except Staff.DoesNotExist:
        return Response({
            "status": False,
            "message": "Staff not found"
        })

    # Get today's day name
    today = datetime.datetime.now().strftime("%A")

    # Get subjects this staff teaches
    staff_subjects = [s.strip() for s in (staff.subjects or "").split(",") if s.strip()]

    # Get timetable for today for this staff
    from subject.models import Subject
    department_subjects = Subject.objects.filter(
        department=staff.department
    )

    # Build today's schedule from generated timetable logic
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    periods = 8
    ROOMS = ["Room 101", "Room 102", "Room 201", "Room 202", "Lab 1", "Lab 2", "Lab 102", "Room 301"]

    today_schedule = []
    total_periods = 0
    active_days = 0

    all_staff = list(Staff.objects.filter(department=staff.department).order_by('id'))
    all_subjects = list(department_subjects.order_by('id'))

    if all_subjects and all_staff:
        import random

        subject_keys = [s.name for s in all_subjects]

        for d_index, day in enumerate(days):
            rng = random.Random(d_index + 42)
            day_subjects = subject_keys.copy()
            rng.shuffle(day_subjects)

            day_periods = []
            used_slots = {}
            staff_list = [s for s in all_staff]

            for p in range(periods):
                sub_name = day_subjects[p % len(day_subjects)]
                staff_index = (d_index + p) % len(staff_list)
                assigned_staff = staff_list[staff_index]

                if assigned_staff.id == staff.id:
                    sub_obj = next((s for s in all_subjects if s.name == sub_name), None)
                    is_lab = "lab" in sub_name.lower()
                    room = ROOMS[(d_index + p) % len(ROOMS)]

                    period_data = {
                        "period": p + 1,
                        "subject": sub_name,
                        "year": f"{sub_obj.year} Year" if sub_obj and hasattr(sub_obj, 'year') else "",
                        "room": room,
                        "is_lab": is_lab
                    }

                    if day == today:
                        today_schedule.append(period_data)

                    day_periods.append(period_data)
                    total_periods += 1

            if day_periods:
                active_days += 1

    return Response({
        "status": True,
        "message": "Staff dashboard fetched successfully",
        "data": {
            "staff": {
                "id": staff.id,
                "name": staff.name,
                "email": staff.email,
                "phone": staff.phone if hasattr(staff, 'phone') else "",
                "department": staff.department.name if staff.department else "",
                "department_type": str(staff.department.type) if staff.department else "",
                "status": staff.status,
                "joined": str(staff.created_at) if hasattr(staff, 'created_at') else ""
            },
            "stats": {
                "total_periods": total_periods,
                "today_classes": len(today_schedule),
                "subjects": len(staff_subjects),
                "active_days": f"{active_days}/6"
            },
            "today": today,
            "today_schedule": today_schedule
        }
    })