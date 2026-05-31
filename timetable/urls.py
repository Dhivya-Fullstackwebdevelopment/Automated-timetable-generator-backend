from django.urls import path
from .views import dashboard, admin_login, generate_timetable, staff_dashboard, staff_login, staff_full_timetable

urlpatterns = [
    path('generate/', generate_timetable),
    path('admin-login/', admin_login),
    path('dashboard/', dashboard),
    path('staff-login/', staff_login),
    path('staff-dashboard/<int:staff_id>/', staff_dashboard),
    # timetable/urls.py
# timetable/urls.py

path(
    "staff-full-timetable/<int:staff_id>/",
    staff_full_timetable
),
]