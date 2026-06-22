from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Mailing, MailingLog

class MailingListView(ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

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

class MailingUpdateView(UpdateView):
    model = Mailing
    fields = ['message', 'clients', 'start_date', 'end_date', 'status']
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:list')

class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:list')

from django.shortcuts import get_object_or_404, redirect
from django.views import View
from .services import send_mailing_now

class MailingSendView(View):
    """Контроллер для ручного запуска рассылки из браузера"""
    def post(self, request, *args, **kwargs):
        mailing = get_object_or_404(Mailing, pk=self.kwargs.get('pk'))
        send_mailing_now(mailing)
        return redirect('mailings:detail', pk=mailing.pk)


from django.views.generic import TemplateView
from mailings.models import Mailing
from clients.models import Client


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
