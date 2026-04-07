from django.db import models
from department.models import Department

class Staff(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SICK', 'Sick Leave'),
        ('EMERGENCY', 'Emergency Leave'),
        ('RESIGNED', 'Resigned'),
    ]

    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    subjects = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    def __str__(self):
        return self.name