from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.exceptions import PermissionDenied
from .models import Client

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Менеджеры').exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'

class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:list')

    def test_func(self):
        return self.get_object().owner == self.request.user or self.request.user.is_superuser

class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:list')

    def test_func(self):
        return self.get_object().owner == self.request.user or self.request.user.is_superuser

