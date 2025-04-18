from django.urls import path, include

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('home/', include('home.urls'), name='home'),
    path('', include('user_login.urls'), name='personal_account'),
]
