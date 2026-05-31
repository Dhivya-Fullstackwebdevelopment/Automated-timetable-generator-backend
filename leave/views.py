from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import LeaveRequest
from .serializers import LeaveSerializer
from staff.models import Staff
from django.utils import timezone


def auto_activate_expired_leaves():
    today = timezone.now().date()
    expired = LeaveRequest.objects.select_related('staff').filter(
        to_date__lt=today,
        leave_type__in=["SICK", "EMERGENCY"],   # ✅ never reactivate RESIGNED
        staff__status__in=["SICK", "EMERGENCY"]
    )
    for leave in expired:
        leave.staff.status = "ACTIVE"
        leave.staff.save()


@api_view(['POST'])
def apply_leave(request):

    auto_activate_expired_leaves()  # ✅ check on every request

    serializer = LeaveSerializer(data=request.data)

    if serializer.is_valid():
        leave = serializer.save()

        if leave.leave_type == "SICK":
            leave.staff.status = "SICK"
        elif leave.leave_type == "EMERGENCY":
            leave.staff.status = "EMERGENCY"
        elif leave.leave_type == "RESIGNED":
            leave.staff.status = "RESIGNED"

        leave.staff.save()

        return Response({
            "status": True,
            "message": "Leave applied successfully",
            "data": serializer.data
        })

    return Response({
        "status": False,
        "errors": serializer.errors
    })


@api_view(['GET'])
def leave_list(request):

    auto_activate_expired_leaves()  # ✅ check on every request

    leaves = LeaveRequest.objects.select_related('staff').all().order_by('-id')
    serializer = LeaveSerializer(leaves, many=True)

    return Response({
        "status": True,
        "data": serializer.data
    })

@api_view(['POST'])
def resign_staff(request):
    staff_id = request.data.get("staff_id")

    if not staff_id:
        return Response({
            "status": False,
            "message": "staff_id is required"
        })

    try:
        staff = Staff.objects.get(id=staff_id)
    except Staff.DoesNotExist:
        return Response({
            "status": False,
            "message": "Staff not found"
        })

    # ✅ Check already resigned
    if staff.status == "RESIGNED":
        return Response({
            "status": False,
            "message": f"{staff.name} is already resigned"
        })

    from django.utils.timezone import now
    today = now().date()

    # ✅ Create leave record — reason, from_date, to_date are optional/auto
    leave = LeaveRequest.objects.create(
        staff=staff,
        leave_type="RESIGNED",
        from_date=today,   # auto set today
        to_date=today,     # auto set today
        reason=""          # blank — not needed for resign
    )

    # ✅ Update staff status
    staff.status = "RESIGNED"
    staff.save()

    return Response({
        "status": True,
        "message": f"{staff.name} has been resigned successfully",
        "data": {
            "staff_id": staff.id,
            "name": staff.name,
            "department": staff.department.name if staff.department else "",
            "status": staff.status,
            "resigned_on": str(today),
        }
    })