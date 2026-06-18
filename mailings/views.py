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

