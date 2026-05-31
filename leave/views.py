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