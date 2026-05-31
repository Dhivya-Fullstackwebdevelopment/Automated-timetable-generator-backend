from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Staff
from .serializers import StaffSerializer
from django.utils import timezone  # ✅ missing import added


def auto_activate_expired_leaves():
    from leave.models import LeaveRequest
    today = timezone.now().date()
    expired = LeaveRequest.objects.select_related('staff').filter(
        to_date__lt=today,
        leave_type__in=["SICK", "EMERGENCY"],
        staff__status__in=["SICK", "EMERGENCY"]
    )
    for leave in expired:
        leave.staff.status = "ACTIVE"
        leave.staff.save()


@api_view(['POST'])
def add_staff(request):
    serializer = StaffSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Staff created successfully",
            "data": serializer.data
        }, status=201)

    return Response({
        "status": "failure",
        "message": "Creation failed",
        "errors": serializer.errors
    }, status=400)


@api_view(['GET'])  # ✅ missing decorator added
def get_staff(request):
    auto_activate_expired_leaves()  # ✅ auto activate on every list call
    staff = Staff.objects.select_related('department').all()
    serializer = StaffSerializer(staff, many=True)
    return Response({
        "status": "success",
        "message": "Staff fetched successfully",
        "data": serializer.data
    })


@api_view(['PUT'])
def update_staff(request, pk):
    try:
        staff = Staff.objects.get(pk=pk)
    except Staff.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Staff not found"
        }, status=404)

    serializer = StaffSerializer(staff, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Staff updated successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failure",
        "message": "Update failed",
        "errors": serializer.errors
    }, status=400)


@api_view(['DELETE'])
def delete_staff(request, pk):
    try:
        staff = Staff.objects.get(pk=pk)
        staff.delete()
        return Response({
            "status": "success",
            "message": "Staff deleted successfully"
        })
    except Staff.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Staff not found"
        }, status=404)