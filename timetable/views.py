import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from subject.models import Subject
from staff.models import Staff


@api_view(['POST'])
def generate_timetable(request):
    department = request.data.get("department")
    year = request.data.get("year")
    semester = request.data.get("semester")

    # ✅ Get subjects
    subjects = Subject.objects.filter(
        department=department,
        year=year,
        semester=semester
    )

    # ✅ Get staff
    staff_list = Staff.objects.filter(department=department, status="ACTIVE")

    # ✅ Map subject → staff
    subject_staff_map = {}

    for sub in subjects:
        matched_staff = []

        for staff in staff_list:
            if sub.name.lower() in staff.subjects.lower():
                matched_staff.append(staff)

        if matched_staff:
            subject_staff_map[sub.name] = matched_staff

    # ❌ Check missing staff
    missing = [sub.name for sub in subjects if sub.name not in subject_staff_map]

    if missing:
        return Response({
            "status": False,
            "message": f"No staff for subjects: {', '.join(missing)}"
        })

    # ✅ Generate timetable
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    periods = 8

    timetable = []
    used_slots = {}

    for day in days:
        row = []

        for p in range(periods):
            sub = random.choice(list(subject_staff_map.keys()))
            staff_choices = subject_staff_map[sub]

            assigned = None

            for _ in range(10):  # try 10 times to avoid conflict
                staff = random.choice(staff_choices)
                key = f"{staff.id}-{day}-{p}"

                if key not in used_slots:
                    used_slots[key] = True
                    assigned = staff
                    break

            if assigned:
                row.append({
                    "subject": sub,
                    "staff": assigned.name
                })
            else:
                row.append({
                    "subject": "Free",
                    "staff": ""
                })

        timetable.append({
            "day": day,
            "periods": row
        })

    return Response({
        "status": True,
        "data": timetable
    })