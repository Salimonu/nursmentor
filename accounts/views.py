from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import CreateView

from .models import User


class SignupView(CreateView):
    model = User
    template_name = 'accounts/signup.html'
    fields = ['username', 'email', 'role', 'password']

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(self.request, user)
        return redirect(reverse('home'))


def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.role == 'admin':
            return redirect('admin:index')
        if request.user.role == 'teacher':
            return redirect('teacher_dashboard')
        return redirect('student_dashboard')
    return render(request, 'accounts/home.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser or user.role == 'admin':
                    return redirect('admin:index')
                if user.role == 'teacher':
                    return redirect('teacher_dashboard')
                return redirect('student_dashboard')
    else:
        form = AuthenticationForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def student_dashboard(request):
    return render(request, 'accounts/dashboard.html', {'role': 'Student'})


def teacher_dashboard(request):
    return render(request, 'accounts/dashboard.html', {'role': 'Teacher'})
