from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('active_appointments/', views.active_appointments, name='active_appointment'),
    path("cancel/<int:appointment_id>/", views.cancel_appointment, name="cancel_appointment"),
    path('history/', views.appointment_history, name='history'),
]