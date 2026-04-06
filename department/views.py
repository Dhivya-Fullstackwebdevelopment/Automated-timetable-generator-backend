from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Department
from .serializers import DepartmentSerializer


# Add Department
@api_view(['POST'])
def add_department(request):
    serializer = DepartmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Department created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "status": "failure",
        "message": "Creation failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


#Get all departments
@api_view(['GET'])
def get_departments(request):
    departments = Department.objects.all()
    serializer = DepartmentSerializer(departments, many=True)

    return Response({
        "status": "success",
        "message": "Departments fetched successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)


#Update Department
@api_view(['PUT'])
def update_department(request, pk):
    try:
        dept = Department.objects.get(pk=pk)
    except Department.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Department not found"
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = DepartmentSerializer(dept, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Department updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "status": "failure",
        "message": "Update failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# Delete Department
@api_view(['DELETE'])
def delete_department(request, pk):
    try:
        dept = Department.objects.get(pk=pk)
        dept.delete()
        return Response({
            "status": "success",
            "message": "Department deleted successfully"
        }, status=status.HTTP_200_OK)

    except Department.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Department not found"
        }, status=status.HTTP_404_NOT_FOUND)