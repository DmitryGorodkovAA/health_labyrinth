from django.urls import path, include

from user_login import views

urlpatterns = [
    path('', views.login_page, name='login'),
]