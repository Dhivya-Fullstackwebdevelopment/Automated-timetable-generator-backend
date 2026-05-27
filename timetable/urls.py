from django.urls import path
from .views import dashboard, admin_login, generate_timetable

urlpatterns = [
    path('generate/', generate_timetable),
    path('admin-login/', admin_login),
    path('dashboard/', dashboard),
    # path('staff-login/', staff_login),
    # path('staff-dashboard/<int:staff_id>/', staff_dashboard),
]