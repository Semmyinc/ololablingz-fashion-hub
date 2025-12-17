from django.urls import path
from . import views

urlpatterns = [
    
    path("register/", views.register, name='register'),
    path("login/", views.login_user, name='login'),
    path("logout/", views.logout_user, name='logout'),
    path("", views.dashboard, name='dashboard'),
    path("dashboard/", views.dashboard, name='dashboard'),
    path("forgot_password/", views.forgot_password, name='forgot_password'),
    # mail activation
    path("activate/<uidb64>/<token>/", views.activate, name='activate'),
    path("reset_password_validation/<uidb64>/<token>/", views.reset_password_validation, name='reset_password_validation'),
    path("reset_password/", views.reset_password, name='reset_password'),
]

