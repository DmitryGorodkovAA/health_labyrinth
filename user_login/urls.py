from django.urls import path, include

from user_login import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('register/', views.register, name='register'),
    path('', views.personal_account, name='personal_account'),
]