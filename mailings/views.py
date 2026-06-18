from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Mailing

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

        # Сбор аналитики для главной страницы
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='started').count()
        context['unique_clients'] = Client.objects.filter(mailings__isnull=False).distinct().count()

        return context
