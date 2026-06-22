from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Mailing, MailingLog
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from .services import send_mailing_now
from django.views.generic import TemplateView
from mailings.models import Mailing
from clients.models import Client


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Менеджеры').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'


class MailingCreateView(CreateView):
    model = Mailing
    fields = ['message', 'clients', 'start_date', 'end_date', 'status']
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:list')

    def form_valid(self, form):
        # Делаем текущего пользователя владельцем рассылки
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    fields = ['message', 'clients', 'start_date', 'end_date', 'status']
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:list')

    def test_func(self):
        # Менеджер не может редактировать чужие рассылки, только владелец или админ
        return self.get_object().owner == self.request.user or self.request.user.is_superuser


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:list')

    def test_func(self):
        return self.get_object().owner == self.request.user or self.request.user.is_superuser


class MailingSendView(View):
    """Контроллер для ручного запуска рассылки из браузера"""
    def post(self, request, *args, **kwargs):
        mailing = get_object_or_404(Mailing, pk=self.kwargs.get('pk'))
        send_mailing_now(mailing)
        return redirect('mailings:detail', pk=mailing.pk)


@method_decorator(cache_page(60 * 10), name='dispatch')
class HomeView(TemplateView):
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Сбор аналитики для главной страницы
        if user.is_authenticated:
            # Статистика только для ТЕКУЩЕГО вошедшего пользователя
            user_mailings = Mailing.objects.filter(owner=user)
            context['total_mailings'] = user_mailings.count()
            context['active_mailings'] = user_mailings.filter(status='started').count()

            # Количество уникальных клиентов пользователя в рассылках
            context['unique_clients'] = Client.objects.filter(mailings__owner=user).distinct().count()

            # Сбор статистики попыток для этого пользователя
            context['success_logs'] = MailingLog.objects.filter(mailing__owner=user, status='success').count()
            context['failure_logs'] = MailingLog.objects.filter(mailing__owner=user, status='failure').count()
        else:
            # Для неавторизованных пользователей показываем нули или общую статистику
            context['total_mailings'] = 0
            context['active_mailings'] = 0
            context['unique_clients'] = 0
            context['success_logs'] = 0
            context['failure_logs'] = 0

        return context

class MailingToggleStatusView(LoginRequiredMixin, View):
    """Позволяет менеджеру принудительно завершить/отключить рассылку"""
    def post(self, request, pk):
        if not (request.user.is_superuser or request.user.groups.filter(name='Менеджеры').exists()):
            raise PermissionDenied
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = 'completed'
        mailing.save()
        return redirect('mailings:list')
