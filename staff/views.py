from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Staff
from .serializers import StaffSerializer


# ➕ Add Staff
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


# 📋 List Staff
@api_view(['GET'])
def get_staff(request):
    staff = Staff.objects.select_related('department').all()
    serializer = StaffSerializer(staff, many=True)

    return Response({
        "status": "success",
        "message": "Staff fetched successfully",
        "data": serializer.data
    })


# ✏️ Update Staff
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


# ❌ Delete Staff
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