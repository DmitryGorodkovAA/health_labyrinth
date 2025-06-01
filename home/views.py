import json
import profile
import random


import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from user_login.models import User, Forecast, PointForecast
from rest_framework import serializers

import json
from django.shortcuts import render, redirect
from django import forms

import joblib
import pandas as pd
from pathlib import Path

HEALTH_ADVICE_LEVELS = [
    # -----------------------
    # УРОВЕНЬ 1: БАЗОВЫЕ РЕКОМЕНДАЦИИ
    # -----------------------

    {
        "title": "Бросьте курить (базовый уровень)",
        "description": (
            "Курение повышает риск сердечно-сосудистых заболеваний. "
            "Отказ от курения даже на несколько месяцев помогает снизить воспаление сосудов."
        ),
        "effects": {
            "stroke": 30,
            "arrhythmia": 20,
            "ischemic_heart_disease": 25,
            "heart_failure": 15,
        },
        "relevant": lambda d: d["smoking"] == 1,
        "level": 1,
    },
    {
        "title": "Контролируйте потребление алкоголя (базовый уровень)",
        "description": (
            "Чрезмерное употребление алкоголя повышает риск гипертонии и инсульта. "
            "Попробуйте ограничиться максимум 1-2 стандартными порциями в неделю."
        ),
        "effects": {
            "hypertension": 15,
            "arrhythmia": 10,
            "stroke": 10,
        },
        "relevant": lambda d: d["alcohol"] > 0,
        "level": 1,
    },
    {
        "title": "Добавьте лёгкую физическую активность (базовый уровень)",
        "description": (
            "Добавьте по 15–20 минут быстрой ходьбы или простых упражнений 3 раза в неделю. "
            "Это уже поможет улучшить кровообращение и снизить нагрузку на сердце."
        ),
        "effects": {
            "stroke": 10,
            "ischemic_heart_disease": 15,
            "hypertension": 10,
            "heart_failure": 5,
        },
        "relevant": lambda d: d["activity_level"] < 2,
        "level": 1,
    },
    {
        "title": "Снизьте допустимый вес (базовый уровень)",
        "description": (
            "Небольшая корректировка рациона для постепенного снижения веса (1–2 кг в месяц) "
            "способствует улучшению давления и уменьшает нагрузку на сердце."
        ),
        "effects": {
            "hypertension": 15,
            "heart_failure": 10,
            "ischemic_heart_disease": 10,
        },
        "relevant": lambda d: d["weight"] / ((d["height"] / 100) ** 2) > 25,
        "level": 1,
    },
    {
        "title": "Регулярный сон минимум 7 часов (базовый уровень)",
        "description": (
            "Недостаток сна (< 6 часов) повышает уровень кортизола и может спровоцировать "
            "аритмии и повышение давления. Стремитесь к 7–8 часам сна."
        ),
        "effects": {
            "arrhythmia": 10,
            "hypertension": 10,
        },
        "relevant": lambda d: d["sleep_hours"] < 6,
        "level": 1,
    },
    {
        "title": "Простые дыхательные практики для снижения стресса (уровень 1)",
        "description": (
            "Потратьте 5 минут в день на глубокое дыхание: вдох на 4 с, задержка на 4 с, выдох — 6 с. "
            "Это уменьшит уровень стресса и поможет нормализовать давление."
        ),
        "effects": {
            "hypertension": 10,
            "ischemic_heart_disease": 5,
        },
        "relevant": lambda d: d["stress_level"] >= 3,
        "level": 1,
    },
    {
        "title": "Добавьте больше овощей и фруктов (уровень 1)",
        "description": (
            "Старайтесь, чтобы минимум половина тарелки была заполнена овощами и фруктами. "
            "Это обогатит организм клетчаткой и антиоксидантами."
        ),
        "effects": {
            "ischemic_heart_disease": 10,
            "hypertension": 5,
            "stroke": 5,
        },
        "relevant": lambda d: True,  # базово полезно для всех
        "level": 1,
    },
    {
        "title": "Пейте достаточное количество воды (уровень 1)",
        "description": (
            "Цель — не меньше 1.5–2 литров чистой воды в день. "
            "Помогает поддерживать кровяное давление и улучшает обмен веществ."
        ),
        "effects": {
            "hypertension": 5,
            "ischemic_heart_disease": 5,
        },
        "relevant": lambda d: True,
        "level": 1,
    },


    # -----------------------
    # УРОВЕНЬ 2: УСИЛЕННЫЕ РЕКОМЕНДАЦИИ
    # -----------------------

    {
        "title": "Полный отказ от курения (уровень 2)",
        "description": (
            "Если вы бросили курить недавно, продолжайте не возвращаться к привычке. "
            "Участвуйте в группах поддержки или пользуйтесь никотинозаместительными средствами."
        ),
        "effects": {
            "stroke": 40,
            "arrhythmia": 30,
            "ischemic_heart_disease": 35,
            "heart_failure": 25,
        },
        "relevant": lambda d: d["smoking"] == 1,
        "level": 2,
    },
    {
        "title": "Ограничьте алкоголь до минимум (уровень 2)",
        "description": (
            "Не более 1 стандартной порции алкоголя в неделю. "
            "Лучше вовсе отказаться от напитков, содержащих алкоголь."
        ),
        "effects": {
            "hypertension": 30,
            "arrhythmia": 25,
            "stroke": 20,
        },
        "relevant": lambda d: d["alcohol"] > 0,
        "level": 2,
    },
    {
        "title": "Активные тренировки — 30 минут 5 раз в неделю (уровень 2)",
        "description": (
            "Добавьте кардио упражнения (быстрая ходьба, лёгкий бег, велосипед). "
            "Не менее 150 минут в неделю умеренной активности."
        ),
        "effects": {
            "stroke": 25,
            "ischemic_heart_disease": 35,
            "hypertension": 30,
            "heart_failure": 20,
        },
        "relevant": lambda d: d["activity_level"] < 3,
        "level": 2,
    },
    {
        "title": "Сбалансированная диета с контролем калорий (уровень 2)",
        "description": (
            "Уменьшите потребление простых углеводов и насыщенных жиров. "
            "Сосредоточьтесь на кашах, нежирном белке и большом количестве овощей."
        ),
        "effects": {
            "hypertension": 30,
            "ischemic_heart_disease": 30,
            "heart_failure": 25,
            "stroke": 15,
        },
        "relevant": lambda d: d["weight"] / ((d["height"] / 100) ** 2) > 27,
        "level": 2,
    },
    {
        "title": "Контроль сна до 7–8 часов (уровень 2)",
        "description": (
            "Груднее планируйте распорядок: ложитесь не позднее 23:00, избегайте экранов за час до сна. "
            "Используйте расслабляющие ритуалы (тёплая ванна, чтение)."
        ),
        "effects": {
            "arrhythmia": 20,
            "hypertension": 20,
            "ischemic_heart_disease": 10,
        },
        "relevant": lambda d: d["sleep_hours"] < 7,
        "level": 2,
    },
    {
        "title": "Релаксационные техники — медитация (уровень 2)",
        "description": (
            "10–15 минут медитации ежедневно или йога 2–3 раза в неделю. "
            "Это снижает уровень кортизола и нормализует давление."
        ),
        "effects": {
            "hypertension": 20,
            "ischemic_heart_disease": 15,
            "stroke": 10,
        },
        "relevant": lambda d: d["stress_level"] >= 3,
        "level": 2,
    },
    {
        "title": "Периодический контроль ИМТ и окружности талии (уровень 2)",
        "description": (
            "Измеряйте вес и окружность талии каждые 2 недели. "
            "Если окружность талии > 102 см (мужчины) или > 88 см (женщины) — нужен более жёсткий контроль рациона."
        ),
        "effects": {
            "hypertension": 25,
            "ischemic_heart_disease": 20,
            "heart_failure": 15,
        },
        "relevant": lambda d: d["weight"] / ((d["height"] / 100) ** 2) > 25,
        "level": 2,
    },
    {
        "title": "Регулярное потребление капусты и листовых овощей (уровень 2)",
        "description": (
            "Добавьте в рацион брокколи, шпинат, салатные листья 3–4 раза в неделю. "
            "Это обогатит организм нитратами и фолатами, ухудшающими артериальную гипертензию."
        ),
        "effects": {
            "hypertension": 20,
            "ischemic_heart_disease": 15,
        },
        "relevant": lambda d: True,
        "level": 2,
    },


    # -----------------------
    # УРОВЕНЬ 3: ИНТЕНСИВНЫЕ РЕКОМЕНДАЦИИ
    # -----------------------

    {
        "title": "Полная программа отказа от табака (уровень 3)",
        "description": (
            "Пройдите курс у врача-нарколога или используйте специализированную клинику "
            "для полной реабилитации от никотина (групповая терапия, медикаменты)."
        ),
        "effects": {
            "stroke": 50,
            "arrhythmia": 40,
            "ischemic_heart_disease": 45,
            "heart_failure": 30,
        },
        "relevant": lambda d: d["smoking"] == 1,
        "level": 3,
    },
    {
        "title": "Абсолютный отказ от алкоголя (уровень 3)",
        "description": (
            "Полный отказ от любых спиртных напитков. "
            "Если самостоятельное ограничение не помогает, обратитесь к психотерапевту."
        ),
        "effects": {
            "hypertension": 40,
            "arrhythmia": 35,
            "stroke": 30,
            "ischemic_heart_disease": 25,
        },
        "relevant": lambda d: d["alcohol"] > 0,
        "level": 3,
    },
    {
        "title": "Интенсивные кардио-тренировки — 45–60 минут 5–6 раз в неделю (уровень 3)",
        "description": (
            "Занимайтесь бегом, плаванием или велоспортом не менее 200 минут в неделю. "
            "Добавьте интервальные тренировки для повышения выносливости."
        ),
        "effects": {
            "stroke": 35,
            "ischemic_heart_disease": 45,
            "hypertension": 35,
            "heart_failure": 30,
        },
        "relevant": lambda d: d["activity_level"] < 4,
        "level": 3,
    },
    {
        "title": "Строгая низкокалорийная диета (уровень 3)",
        "description": (
            "Сократите потребление калорий на 500–700 ккал в день для быстрого (до 1 –1.5 кг/неделю) "
            "снижения веса. Контролируйте макронутриенты: белок 1.2–1.5 г/кг, минимум углеводов, "
            "низкий гликемический индекс."
        ),
        "effects": {
            "hypertension": 40,
            "ischemic_heart_disease": 35,
            "heart_failure": 30,
            "stroke": 20,
        },
        "relevant": lambda d: d["weight"] / ((d["height"] / 100) ** 2) > 27,
        "level": 3,
    },
    {
        "title": "Сон 8–9 часов и режим «глубокого отдыха» (уровень 3)",
        "description": (
            "Организуйте «гигиену сна»: фиксированный график (ложитесь не позже 22:00, вставайте до 7:00), "
            "отказ от гаджетов за 2 часа до сна, глубокое расслабление (медитация, ча мелиссы)."
        ),
        "effects": {
            "arrhythmia": 30,
            "hypertension": 25,
            "ischemic_heart_disease": 15,
        },
        "relevant": lambda d: d["sleep_hours"] < 8,
        "level": 3,
    },
    {
        "title": "Интенсивные практики управления стрессом (уровень 3)",
        "description": (
            "Посещайте психотерапевта 1 раз в неделю, проходите курсы когнитивно-поведенческой терапии или "
            "биоуправления биообратной связью. "
            "Регулярно занимайтесь глубокими медитациями и практиками майндфулнес."
        ),
        "effects": {
            "hypertension": 30,
            "ischemic_heart_disease": 25,
            "stroke": 15,
        },
        "relevant": lambda d: d["stress_level"] >= 4,
        "level": 3,
    },
    {
        "title": "Ежеквартальные медицинские обследования (уровень 3)",
        "description": (
            "Проходите полный чек-ап у кардиолога, сдавайте кровь на липиды, проверяйте ЭКГ и ЭХОКГ каждые 3 месяца. "
            "Раннее выявление отклонений помогает быстро скорректировать лечение и снизить риск."
        ),
        "effects": {
            "ischemic_heart_disease": 20,
            "hypertension": 20,
            "heart_failure": 15,
            "stroke": 10,
        },
        "relevant": lambda d: d["age"] >= 45,
        "level": 3,
    },
    {
        "title": "Специальная диета DASH или средиземноморская диета (уровень 3)",
        "description": (
            "Следуйте принципам DASH: много овощей, фруктов, нежирных молочных продуктов, "
            "цельнозерновых, орехов. Ограничьте красное мясо и рафинированные продукты."
        ),
        "effects": {
            "hypertension": 35,
            "ischemic_heart_disease": 30,
            "stroke": 20,
        },
        "relevant": lambda d: True,
        "level": 3,
    },
]

def get_personal_health_advice(user_data):
    relevant_advice = []
    for advice in HEALTH_ADVICE_LEVELS:
        try:
            if advice['relevant'](user_data):
                relevant_advice.append({
                    "title": advice["title"],
                    "description": advice["description"],
                    "effects": advice["effects"],
                    'level': advice["level"],
                })
        except Exception as e:
            continue
    return relevant_advice

YEARS = 20
diseases = ['stroke', 'arrhythmia', 'ischemic_heart_disease', 'hypertension', 'heart_failure']
FEATURES = ['age', 'sex', 'height', 'weight', 'activity_level', 'sleep_hours', 'smoking', 'alcohol', 'stress_level', 'bmi']
BASE_DIR = Path(__file__).resolve().parent
models = {}
for disease in diseases:
    models[disease] = []
    for year in range(1, YEARS + 1):
        model_path = BASE_DIR / 'models' / f'{disease}_year{year}.joblib'
        models[disease].append(joblib.load(model_path))

def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)
scaler = joblib.load(BASE_DIR / 'models' / 'scaler.joblib')


def predict_risks(user_data: dict) -> dict:
    df = pd.DataFrame([user_data])
    df['bmi'] = calculate_bmi(df['weight'], df['height'])
    X = scaler.transform(df[FEATURES])

    results = {}
    for disease in diseases:
        probs = []
        for model in models[disease]:
            prob = model.predict_proba(X)[0][1]
            probs.append(round(prob * 100, 2))
        results[disease] = probs

    return results


class HealthForm(forms.Form):
    age = forms.IntegerField(
        min_value=0,
        max_value=120,
        label='Возраст',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите возраст'
        })
    )
    sex = forms.ChoiceField(
        choices=[(0, 'Мужской'), (1, 'Женский')],
        label='Пол',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    height = forms.FloatField(
        min_value=50,
        max_value=250,
        label='Рост (см)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите рост'
        })
    )
    weight = forms.FloatField(
        min_value=20,
        max_value=300,
        label='Вес (кг)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите вес'
        })
    )
    activity_level = forms.ChoiceField(
        choices=[(i, f'Уровень {i}') for i in range(1, 6)],
        label='Уровень активности',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sleep_hours = forms.FloatField(
        min_value=0,
        max_value=24,
        label='Часы сна в день',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например, 8'
        })
    )
    smoking = forms.BooleanField(
        required=False,
        label='Курите?',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    alcohol = forms.BooleanField(
        required=False,
        label='Употребляете алкоголь?',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    stress_level = forms.ChoiceField(
        choices=[(i, f'Уровень {i}') for i in range(1, 6)],
        label='Уровень стресса',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

# Форма для ввода пользовательских данных
# class HealthForm(forms.Form):
#     age = forms.IntegerField(min_value=0, max_value=120)
#     sex = forms.ChoiceField(choices=[(0, 'Мужской'), (1, 'Женский')])
#     height = forms.FloatField(min_value=50, max_value=250)
#     weight = forms.FloatField(min_value=20, max_value=300)
#     activity_level = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)])
#     sleep_hours = forms.FloatField(min_value=0, max_value=24)
#     smoking = forms.BooleanField(required=False)
#     alcohol = forms.BooleanField(required=False)
#     stress_level = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)])


def forecast(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    user = request.user

    initial = {
        'age':            user.age,
        'sex':            0 if user.gender == 'M' else 1,
        'height':         user.height,
        'weight':         user.weight,
        'activity_level': user.activity_level,
        'sleep_hours':    user.sleep_hours,
        'smoking':        user.smoking,
        'alcohol':        user.alcohol,
        'stress_level':   user.stress_level,
    }

    form = HealthForm(request.POST or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data

        user.age            = cd['age']
        user.gender         = 'M' if int(cd['sex']) == 0 else 'F'
        user.height         = cd['height']
        user.weight         = cd['weight']
        user.activity_level = int(cd['activity_level'])
        user.sleep_hours    = cd['sleep_hours']
        user.smoking        = cd['smoking']
        user.alcohol        = cd['alcohol']
        user.stress_level   = int(cd['stress_level'])
        user.save()

        user_data = {
            'age': cd['age'],
            'sex': int(cd['sex']),
            'height': cd['height'],
            'weight': cd['weight'],
            'activity_level': int(cd['activity_level']),
            'sleep_hours': cd['sleep_hours'],
            'smoking': int(cd['smoking']),
            'alcohol': int(cd['alcohol']),
            'stress_level': int(cd['stress_level']),
        }

        Forecast.objects.filter(user=user, is_deleted=False).update(is_deleted=True)

        predictions = predict_risks(user_data)
        for disease, probs in predictions.items():
            fc = Forecast.objects.create(user=user, name=disease)
            start_age = user_data['age']
            for i, p in enumerate(probs, start=1):
                PointForecast.objects.create(
                    forecast=fc,
                    age=start_age + i,
                    percent=p
                )

        return redirect('forecasts')

    forecasts = user.forecast.filter(is_deleted=False)
    forecasts_data = []
    for f_obj in forecasts:
        points = f_obj.points.order_by('age')
        forecasts_data.append({
            'id':     f_obj.id,
            'name':   f_obj.name,
            'points': json.dumps([{'age': pt.age, 'percent': pt.percent} for pt in points])
        })

    print(forecasts_data)
    advice_list = get_personal_health_advice(initial)
    print(advice_list)


    return render(request, 'digital_profile.html', {
        'title': 'Прогнозы',
        'user': user,
        'forecasts': forecasts_data,
        'form': form,
        'advice_list':advice_list
    })


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
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500
        )


