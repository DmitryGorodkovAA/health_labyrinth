import json
import profile
import random

from django.contrib.postgres import serializers
from django.shortcuts import render, redirect
import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from user_login.models import User, Forecast, PointForecast
from rest_framework import serializers



# Create your views here.

def lk(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'lk.html', context={'user': request.user})

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

    print(forecasts_data)

    return render(request, 'digital_profile.html', {
        'title': 'Прогнозы',
        'user': user,
        'forecasts': forecasts_data
    })

def gen_individual_plan(request, user_id):
    user = get_object_or_404(User, id=user_id)

    prog = ["Болезнь Альцгеймера", "Болезнь Паркинсона", "Сосудистая деменция", "Ишемическая болезнь сердца", "Инсульт", "Сердечная недостаточность", "Рак лёгких", "Рак молочной железы", "Рак простаты", "Рак толстой кишки", "Лейкемия", "Остеопороз", "Ревматоидный артрит", "Сахарный диабет 2 типа", "Хроническая почечная недостаточность", "Хроническая обструктивная болезнь лёгких (ХОБЛ)"]

    for point in prog:
        forecast = Forecast(user=user, name=point)
        forecast.save()
        percent = random.randint(5, 10)
        print(point, percent)

        for age in range(user.age, user.age + 20):
            print(user, age)
            pointForecast = PointForecast(forecast=forecast, percent=percent, age=age)
            pointForecast.save()
            percent += random.randint(2, 5)

    return HttpResponse('asd')



def user_profile_update(request):
    if not request.user.is_authenticated:
        return redirect('/login')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


@require_http_methods(["POST"])  # Разрешаем только POST-запросы
def user_profile_update(request):
    try:
        data = json.loads(request.body)

        response_data = {
            "status": "success",
            "message": "Data processed successfully",
            "received_data": data
        }

        return JsonResponse(response_data, status=200)

    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON format"},
            status=400
        )

    except Exception as e:
        # Обработка других исключений
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500
        )


