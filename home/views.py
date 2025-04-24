import random

from django.shortcuts import render, redirect

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from user_login.models import User, Forecast, PointForecast


# Create your views here.


def home(request):

    return render(request, 'home.html', context={'title': 'Домашняя страница'})


def individual_plan(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    user = User.objects.get(id=request.user.id)

    return render(request, 'individual_plan.html', context={
        'title': 'Индивидуальный план',
        'firstname': user.first_name,
        'lastname': user.last_name,
        'gender': user.gender,})

def digital_profile(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    return render(request, 'digital_profile.html')

def forecast(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    user = User.objects.get(id=request.user.id)
    forecasts = user.forecast.all()

    print(list(forecasts))

    forecasts_final = []

    for forecast in forecasts:
        forecasts_final.append({'name': forecast.name, 'points': forecast.points.all()})


    return render(request, 'digital_profile.html', context={'title' : 'Предсказания', 'user': user, 'forecasts': forecasts_final})

def gen_individual_plan(request, user_id):
    user = get_object_or_404(User, id=user_id)

    types = ['Сколиоз', 'Рак крови', 'Лейкемия', 'Сердечная недостаточность', 'Болезнь Альцсгеймера']

    for typy in types:
        forecast = Forecast(name=typy, user=user)
        forecast.save()

        last_percent = random.randint(2, 5)
        for yar in range(user.age, user.age + 25):
            point = PointForecast(age=yar, forecast=forecast,  percent=last_percent)

            last_percent += random.randint(1, 3)

            point.save()

    return HttpResponse('Hello, World!')



