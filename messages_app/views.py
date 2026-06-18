from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Message

class MessageListView(ListView):
    model = Message
    template_name = 'messages_app/message_list.html'
    context_object_name = 'messages'

class MessageDetailView(DetailView):
    model = Message
    template_name = 'messages_app/message_detail.html'

class MessageCreateView(CreateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'messages_app/message_form.html'
    success_url = reverse_lazy('messages_app:list')

class MessageUpdateView(UpdateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'messages_app/message_form.html'
    success_url = reverse_lazy('messages_app:list')

class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'messages_app/message_confirm_delete.html'
    success_url = reverse_lazy('messages_app:list')

