from django.contrib.auth import login, logout, authenticate
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
    return render(request, 'user_login.html', {'form': form})

def login_page(request):
    if request.user.is_authenticated:
        return redirect('personal_account')

    if request.method == 'POST':
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('lk')
            else:
                login_form.add_error(None, 'Неверный email или пароль.')
    else:
        login_form = LoginForm()

    form = RegisterForm()
    return render(request, 'user_login.html', context={'title': 'Login', 'login_form': login_form, 'form': form})

def user_login(request):
    register_form = RegisterForm()
    login_form = LoginForm()
    login_error = None

    if request.method == 'POST':
        if request.POST.get('form_type') == 'register':
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save(commit=False)
                user.username = user.email  # или другое поле для username
                user.set_password(register_form.cleaned_data['password'])
                user.save()
                login(request, user)
                return redirect('home')  # куда перенаправить после регистрации
        elif request.POST.get('form_type') == 'login':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data['email']
                password = login_form.cleaned_data['password']
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')
                else:
                    login_error = "Неверный email или пароль."

    context = {
        'register_form': register_form,
        'login_form': login_form,
        'login_error': login_error,
    }
    return render(request, 'user_login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

def personal_account(request):

    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        email = request.user.email

        return render(request, 'personal_account.html', context={
            'title': 'Personal Account',
            'first_name': first_name, 'last_name': last_name, 'email': email})
    else:
        return redirect('login')





