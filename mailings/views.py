from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Mailing, MailingLog
from .forms import MailingForm
from .services import send_mailing_now
from clients.models import Client


@method_decorator(cache_page(60 * 10), name='dispatch')
class HomeView(TemplateView):
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()

        if user.is_authenticated:
            user_mailings = Mailing.objects.filter(owner=user)

            # Перед подсчетом динамически обновляем статусы всех рассылок пользователя
            for m in user_mailings:
                m.update_status()

            # 1. Общее количество всех созданных рассылок пользователя
            context['total_mailings'] = user_mailings.count()

            # 2. Количество активных рассылок строго по условию ТЗ (интервал времени + статус "Запущена")
            context['active_mailings'] = user_mailings.filter(
                start_time__lte=now,
                end_time__gte=now,
                status='started'
            ).count()

            # 3. Количество уникальных получателей (строго по ТЗ: общее число клиентов в системе для этого пользователя)
            context['unique_clients'] = Client.objects.filter(owner=user).count()

            # Статистика логов для Dashboard
            context['success_logs'] = MailingLog.objects.filter(mailing__owner=user, status='success').count()
            context['failure_logs'] = MailingLog.objects.filter(mailing__owner=user, status='failure').count()
        else:
            context['total_mailings'] = 0
            context['active_mailings'] = 0
            context['unique_clients'] = 0
            context['success_logs'] = 0
            context['failure_logs'] = 0

        return context


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Менеджеры').exists():
            queryset = Mailing.objects.all()
        else:
            queryset = Mailing.objects.filter(owner=user)

        # Обновляем статусы рассылок при выводе списка
        for mailing in queryset:
            mailing.update_status()
        return queryset


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'

    # Пересчёт статуса при открытии страницы
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # Вызов динамического пересчета
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def test_func(self):
        return self.get_object().owner == self.request.user or self.request.user.is_superuser


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:list')

    def test_func(self):
        return self.get_object().owner == self.request.user or self.request.user.is_superuser


from django.contrib import messages  # Убедись, что импорт есть вверху файла


class MailingSendView(View):
    """Контроллер для ручного запуска рассылки с проверкой"""

    def post(self, request, *args, **kwargs):
        mailing = get_object_or_404(Mailing, pk=self.kwargs.get('pk'))

        success, message_text = send_mailing_now(mailing)

        if success:
            messages.success(request, message_text)
        else:
            messages.error(request, message_text)

        return redirect('mailings:detail', pk=mailing.pk)


class MailingToggleStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not (request.user.is_superuser or request.user.groups.filter(name='Менеджеры').exists()):
            raise PermissionDenied
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = 'completed'
        mailing.save()
        return redirect('mailings:list')
