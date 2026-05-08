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

    all_staff = list(Staff.objects.filter(
        department=department
    ).order_by('id'))

    if not subjects:
        return Response({
            "status": False,
            "message": "No subjects found"
        })

    if not all_staff:
        return Response({
            "status": False,
            "message": "No staff found"
        })

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
            subject_staff_map[sub.name] = {
                "type": "active",   
                "staff": active_staff
            }
        elif non_active_staff:
            subject_staff_map[sub.name] = {
                "type": "substituted",
                "staff": non_active_staff
            }
        else:
            subject_staff_map[sub.name] = {
                "type": "substituted",
                "staff": all_staff
            }

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

            info = subject_staff_map[sub]
            staff_choices = info["staff"]
            staff_type = info["type"] 

            staff_index = (d_index + p) % len(staff_choices)
            staff = staff_choices[staff_index]

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

                room = ROOMS[(d_index + p) % len(ROOMS)]

                status = staff_type 

                row.append({
                    "subject": sub,
                    "staff": staff.name,
                    "room": room,
                    "year": f"{year} Year",
                    "status": status,
                    "substitute": None if status == "active" else staff.name,
                    "staff_status": staff.status 
                })

        timetable.append({
            "day": day,
            "periods": row
        })

    return Response({
        "status": True,
        "message": "Timetable generated successfully",
        "data": timetable
    })