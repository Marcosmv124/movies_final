
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    else:
        return render(request,'users/profile.html')



#lOGIN 
def login_view(request):
    if request.method == 'POST':
      
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(reverse('index'))
        else:
            # Return an 'invalid login' error message.
            return render(request, 'users/login.html', {'errors':['Invalid Login']})
    else:
        return render(request, 'users/login.html')


#Register

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email', None)  # El email es opcional
        
        # Validar datos básicos
        if not username or not password or not confirm_password:
            return render(request, 'users/register.html', {'errors': ['Todos los campos son obligatorios.']})
        
        if password != confirm_password:
            return render(request, 'users/register.html', {'errors': ['Las contraseñas no coinciden.']})
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'errors': ['El nombre de usuario ya está en uso.']})
        
        # Crear el usuario
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            messages.success(request, 'Usuario registrado exitosamente. Por favor, inicia sesión.')
            return redirect('login')  # Cambia 'login' por el nombre de tu URL para iniciar sesión
        except Exception as e:
            return render(request, 'users/register.html', {'errors': ['Hubo un problema al registrar al usuario.']})
    else:
        return render(request, 'users/register.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))