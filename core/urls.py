from django.urls import path
from . import views # Import views from the current directory (.)

urlpatterns = [
    # Use the landing_view for the root URL
    path('', views.landing_view, name="landing"), 
    
    # Add a specific path for the dashboard
    path('dashboard/', views.dashboard_view, name="dashboard"), 
]