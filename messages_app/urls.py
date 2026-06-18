from django.urls import path
from .apps import MessagesAppConfig
from .views import MessageListView, MessageDetailView, MessageCreateView, MessageUpdateView, MessageDeleteView

app_name = 'messages_app'

urlpatterns = [
    path('', MessageListView.as_view(), name='list'),
    path('<int:pk>/', MessageDetailView.as_view(), name='detail'),
    path('create/', MessageCreateView.as_view(), name='create'),
    path('<int:pk>/update/', MessageUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', MessageDeleteView.as_view(), name='delete'),
]
