import uuid

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
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


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'


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


def request_email_verification(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    if not user.is_email_verified:
        token = str(uuid.uuid4())
        user.email_verification_token = token
        user.save(update_fields=['email_verification_token'])
        verification_link = request.build_absolute_uri(reverse('verify_email', kwargs={'token': token}))
        send_mail(
            'Verify your email',
            f'Hi {user.username},\n\nPlease verify your email by visiting:\n{verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

    return redirect('student_dashboard' if user.role != 'teacher' else 'teacher_dashboard')


def verify_email(request, token):
    user = User.objects.filter(email_verification_token=token).first()
    if user is None:
        return redirect('home')

    user.is_email_verified = True
    user.email_verification_token = ''
    user.save(update_fields=['is_email_verified', 'email_verification_token'])
    return redirect('home')


def student_dashboard(request):
    return render(request, 'accounts/dashboard.html', {'role': 'Student', 'user': request.user})


def teacher_dashboard(request):
    return render(request, 'accounts/dashboard.html', {'role': 'Teacher', 'user': request.user})
