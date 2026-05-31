from django.core.management.base import BaseCommand
from django.utils import timezone
from leave.models import LeaveRequest


class Command(BaseCommand):
    help = "Auto activate staff whose leave has ended"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        expired_leaves = LeaveRequest.objects.select_related('staff').filter(
            to_date__lt=today,
            leave_type__in=["SICK", "EMERGENCY"],
            staff__status__in=["SICK", "EMERGENCY"]
        )

        count = 0
        for leave in expired_leaves:
            leave.staff.status = "ACTIVE"
            leave.staff.save()
            count += 1
            self.stdout.write(f"Activated: {leave.staff.name}")

        self.stdout.write(f"\nTotal activated: {count} staff")