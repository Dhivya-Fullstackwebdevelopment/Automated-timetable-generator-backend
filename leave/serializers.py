from rest_framework import serializers
from .models import LeaveRequest

class LeaveSerializer(serializers.ModelSerializer):

    staff_name = serializers.CharField(
        source='staff.name',
        read_only=True
    )

    class Meta:
        model = LeaveRequest
        fields = '__all__'