from django.urls import path

from home import views

urlpatterns = [
    path('', views.home, name='home'),
    path('individual_plan/', views.individual_plan, name='individual_plan'),
    path('digital_profile/', views.digital_profile, name='digital_profile'),
    path('forecasts/', views.forecast, name='forecasts'),
    path('lk/', views.lk, name='lk'),
    path('gen_individual_plan/<int:user_id>/', views.gen_individual_plan, name='gen_individual_plan'),
]
