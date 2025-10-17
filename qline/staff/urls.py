from django.urls import path
from . import views

urlpatterns = [
    path('service/register/', views.service_register, name='service_register'),
    path('service/register2/', views.service_register2, name='service_register2'), 

    path('login/', views.staff_login, name='staff_login'),

    path('dashboard/<int:org_id>/', views.staff_dashboard, name='staff_dashboard'),
    path('service_edit/', views.staff_edit_service, name='staff_edit_service'),
    path("serve/<int:appointment_id>/", views.staff_serve, name="staff_serve"),
    path("skip/<int:appointment_id>/", views.staff_skip, name="staff_skip"),

    path('appointments/', views.staff_appointments, name='staff_appointments'),
    path('history/', views.staff_history, name='staff_history'),
    path('slots/', views.staff_slots, name='staff_slots'),
    path('notifications/', views.staff_notifications, name='staff_notifications'),
    path('logout/', views.staff_logout, name='staff_logout'),
]
     