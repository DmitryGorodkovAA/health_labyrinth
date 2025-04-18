from django.contrib.auth import login
from django.shortcuts import render, redirect

from .forms import RegisterForm, LoginForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('personal_account')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_page(request):
    login_form = LoginForm()

    return render(request, 'user_login.html', context={'title': 'Login', 'login_form': login_form})

def personal_account(request):

    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        email = request.user.email

        return render(request, 'personal_account.html', context={'title': 'Personal Account', 'first_name': first_name, 'last_name': last_name, 'email': email})
    else:
        return redirect('login')



