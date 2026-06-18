from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import UserCreateForm, UserProfileForm


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = UserCreateForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()  # Автоматически сохраняет пользователя и хеширует пароль
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = 'Добро пожаловать в MailFlow!'
        message = 'Спасибо, что зарегистрировались в нашем сервисе управления рассылками!'
        from_email = getattr(settings, 'EMAIL_HOST_USER', 'noreply@mailflow.ru')
        recipient_list = [user_email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            print(f"Ошибка при отправке письма: {e}")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        # Пользователь редактирует только свой профиль
        return self.request.user


import secrets
from django.shortcuts import render, redirect
from django.contrib import messages


def password_reset_simple(request):
    """Упрощенное восстановление пароля с генерацией нового пароля"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)

            # Генерируем новый случайный пароль из 8 символов
            new_password = secrets.token_urlsafe(6)
            user.set_password(new_password)
            user.save()

            # Отправляем новый пароль на почту (отобразится в терминале PyCharm)
            send_mail(
                subject='Восстановление пароля MailFlow',
                message=f'Ваш старый пароль был сброшен. Новый пароль для входа: {new_password}',
                from_email=getattr(settings, 'EMAIL_HOST_USER', 'noreply@mailflow.ru'),
                recipient_list=[user.email],
                fail_silently=False,
            )

            # Выводим красивое сообщение об успехе на странице входа
            messages.success(request, 'Новый пароль успешно отправлен на ваш Email! Проверьте терминал PyCharm.')
            return redirect('users:login')

        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким Email не найден.')

    return render(request, 'users/password_reset.html')

