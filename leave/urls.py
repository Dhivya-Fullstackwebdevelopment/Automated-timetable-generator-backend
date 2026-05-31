from django.urls import path
from . import views

urlpatterns = [

    path('apply/', views.apply_leave),

    path('list/', views.leave_list),
    path('resign/', views.resign_staff),

]