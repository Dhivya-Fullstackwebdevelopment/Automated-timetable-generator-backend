from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Department
from .serializers import DepartmentSerializer


# ➕ Add Department
@api_view(['POST'])
def add_department(request):
    serializer = DepartmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 📋 Get all departments
@api_view(['GET'])
def get_departments(request):
    departments = Department.objects.all()
    serializer = DepartmentSerializer(departments, many=True)
    return Response(serializer.data)


# ✏️ Update Department
@api_view(['PUT'])
def update_department(request, pk):
    try:
        dept = Department.objects.get(pk=pk)
    except Department.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    serializer = DepartmentSerializer(dept, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ❌ Delete Department
@api_view(['DELETE'])
def delete_department(request, pk):
    try:
        dept = Department.objects.get(pk=pk)
        dept.delete()
        return Response({'message': 'Deleted successfully'})
    except Department.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)