from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Subject
from .serializers import SubjectSerializer


# ➕ Add Subject
@api_view(['POST'])
def add_subject(request):
    serializer = SubjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Subject created successfully",
            "data": serializer.data
        }, status=201)

    return Response({
        "status": "failure",
        "message": "Creation failed",
        "errors": serializer.errors
    }, status=400)


# 📋 List Subjects
@api_view(['GET'])
def get_subjects(request):
    department_id = request.GET.get('department')

    if department_id:
        subjects = Subject.objects.filter(department_id=department_id)
    else:
        subjects = Subject.objects.all()

    serializer = SubjectSerializer(subjects, many=True)

    return Response({
        "status": "success",
        "message": "Subjects fetched successfully",
        "data": serializer.data
    })


# ✏️ Update Subject
@api_view(['PUT'])
def update_subject(request, pk):
    try:
        subject = Subject.objects.get(pk=pk)
    except Subject.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Subject not found"
        }, status=404)

    serializer = SubjectSerializer(subject, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Subject updated successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failure",
        "message": "Update failed",
        "errors": serializer.errors
    }, status=400)


# ❌ Delete Subject
@api_view(['DELETE'])
def delete_subject(request, pk):
    try:
        subject = Subject.objects.get(pk=pk)
        subject.delete()
        return Response({
            "status": "success",
            "message": "Subject deleted successfully"
        })
    except Subject.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Subject not found"
        }, status=404)