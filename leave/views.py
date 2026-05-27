from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import LeaveRequest
from .serializers import LeaveSerializer
from staff.models import Staff


# APPLY LEAVE
@api_view(['POST'])
def apply_leave(request):

    serializer = LeaveSerializer(data=request.data)

    if serializer.is_valid():

        leave = serializer.save()

        # directly update staff status
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

# LEAVE LIST
@api_view(['GET'])
def leave_list(request):

    leaves = LeaveRequest.objects.select_related(
        'staff'
    ).all().order_by('-id')

    serializer = LeaveSerializer(leaves, many=True)

    return Response({
        "status": True,
        "data": serializer.data
    })
