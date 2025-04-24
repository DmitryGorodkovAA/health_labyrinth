import json
import random

from django.shortcuts import render, redirect
import random

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

    forecasts_data = []

    for forecast_obj in forecasts:
        points_data = [
            {
                "age": point.age,
                "percent": point.percent
            }
            for point in forecast_obj.points.all()
        ]

        forecasts_data.append({
            "id": forecast_obj.id,
            "name": forecast_obj.name,
            "points": json.dumps(points_data)
        })

    return render(request, 'digital_profile.html', {
        'title': 'Прогнозы',
        'user': user,
        'forecasts': forecasts_data
    })

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


    print(list(f"{forecste.name}" for forecste in forecasts))
    print(list(f"{forecste.points}" for forecste in forecasts))

