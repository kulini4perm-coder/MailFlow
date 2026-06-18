from django.core.mail import send_mail
from django.conf import settings
from .models import Mailing


def send_mailing_now(mailing: Mailing):
    """Отправляет сообщения всем клиентам в рамках выбранной рассылки"""
    # Собираем email-адреса клиентов рассылки
    recipient_list = [client.email for client in mailing.clients.all()]

    if not recipient_list:
        return 0

    # Изменение статуса на "Запущена"
    mailing.status = 'started'
    mailing.save()

    # Отправление письма
    sent_count = send_mail(
        subject=mailing.message.subject,
        message=mailing.body if hasattr(mailing, 'body') else mailing.message.body,
        from_email=getattr(settings, 'EMAIL_HOST_USER', 'noreply@mailflow.ru'),
        recipient_list=recipient_list,
        fail_silently=False,
    )

    # Изменение статуса на "Завершена" после успешного выполнения
    mailing.status = 'completed'
    mailing.save()

    return sent_count
