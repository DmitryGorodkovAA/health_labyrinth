from django.shortcuts import render, redirect

from user_login.models import User


# Create your views here.


def home(request):

    return render(request, 'home.html', context={'title': 'Домашняя страница'})


def individualplan(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    user = User.objects.get(id=request.user.id)

    return render(request, 'individualplan.html', context={
        'title': 'Индивидуальный план',
        'firstname': user.first_name,
        'lastname': user.last_name,
        'gender': user.gender,})
def digitalprofile(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    return render(request, 'digital_profile.html')

