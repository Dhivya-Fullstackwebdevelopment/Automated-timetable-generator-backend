from django.db import models
from staff.models import Staff

class LeaveRequest(models.Model):

    LEAVE_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SICK', 'Sick Leave'),
        ('EMERGENCY', 'Emergency Leave'),
        ('RESIGNED', 'Resigned'),
    ]

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_CHOICES
    )

    from_date = models.DateField()

    to_date = models.DateField()

    reason = models.TextField()

    proof = models.ImageField(
        upload_to='leave_proofs/',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.staff.name} - {self.leave_type}"