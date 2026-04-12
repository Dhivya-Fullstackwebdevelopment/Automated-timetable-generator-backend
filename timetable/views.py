from rest_framework.decorators import api_view
from rest_framework.response import Response
from subject.models import Subject
from staff.models import Staff

ROOMS = ["Room 101", "Room 102", "Room 201", "Room 202", "Lab 1", "Lab 2"]


@api_view(['POST'])
def generate_timetable(request):
    department = request.data.get("department")
    year = request.data.get("year")
    semester = request.data.get("semester")

    if not department or not year or not semester:
        return Response({
            "status": False,
            "message": "department, year, semester required"
        })

    subjects = list(Subject.objects.filter(
        department=department,
        year=year,
        semester=semester
    ).order_by('id'))

    staff_list = list(Staff.objects.filter(
        department=department,
        status="ACTIVE"
    ).order_by('id'))

    subject_staff_map = {}

    for sub in subjects:
        matched_staff = [
            staff for staff in staff_list
            if sub.name.lower() in staff.subjects.lower()
        ]

        if matched_staff:
            subject_staff_map[sub.name] = matched_staff

    missing = [sub.name for sub in subjects if sub.name not in subject_staff_map]

    if missing:
        return Response({
            "status": False,
            "message": f"No staff for subjects: {', '.join(missing)}"
        })

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    periods = 8

    timetable = []
    used_slots = {}

    subject_keys = list(subject_staff_map.keys())

    for d_index, day in enumerate(days):
        row = []

        for p in range(periods):
            sub_index = (d_index * periods + p) % len(subject_keys)
            sub = subject_keys[sub_index]

            staff_choices = subject_staff_map[sub]
            staff_index = (d_index + p) % len(staff_choices)
            staff = staff_choices[staff_index]

            key = f"{staff.id}-{day}-{p}"

            if key in used_slots:
                row.append({
                    "subject": "Free",
                    "staff": "",
                    "room": "",
                    "year": f"{year} Year"
                })
            else:
                used_slots[key] = True

                room = ROOMS[(d_index + p) % len(ROOMS)]

                row.append({
                    "subject": sub,
                    "staff": staff.name,
                    "room": room,
                    "year": f"{year} Year"
                })

        timetable.append({
            "day": day,
            "periods": row
        })

    return Response({
        "status": True,
        "data": timetable
    })