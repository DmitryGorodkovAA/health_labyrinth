from django.shortcuts import render, redirect

from user_login.models import User


# Create your views here.


def home(request):
    return render(request, 'home.html', context={'title': 'Домашняя страница'})
def individualplan(request):

    return render(request, 'individualplan.html', context={'title': 'Индивидуальный план', 'firstname': "Неважно", 'lastname': "Последнее", 'gender':'Механик'})


