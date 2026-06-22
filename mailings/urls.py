from django.urls import path
from .apps import MailingsConfig
from .views import MailingListView, MailingDetailView, MailingCreateView, MailingUpdateView, MailingDeleteView, \
    MailingSendView, MailingToggleStatusView

app_name = 'mailings'

urlpatterns = [
    path('', MailingListView.as_view(), name='list'),
    path('<int:pk>/', MailingDetailView.as_view(), name='detail'),
    path('create/', MailingCreateView.as_view(), name='create'),
    path('<int:pk>/update/', MailingUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', MailingDeleteView.as_view(), name='delete'),
    path('<int:pk>/send/', MailingSendView.as_view(), name='send'),
    path('<int:pk>/toggle/', MailingToggleStatusView.as_view(), name='toggle_status'),

]
