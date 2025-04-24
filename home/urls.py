from django.urls import path

from home import views

urlpatterns = [
    path('', views.home, name='home'),
    path('individualplan/', views.individualplan, name='individualplan'),
    path('digitalprofile/', views.digitalprofile, name='digitalprofile'),
]
