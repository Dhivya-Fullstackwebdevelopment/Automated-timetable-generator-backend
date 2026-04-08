from django.db import models
from department.models import Department

class Subject(models.Model):
    SEMESTER_CHOICES = [
        ('ODD', 'Odd'),
        ('EVEN', 'Even'),
    ]

    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    hours_per_week = models.IntegerField()
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    year = models.IntegerField()
    is_lab = models.BooleanField(default=False)

    def __str__(self):
        return self.name