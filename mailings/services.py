import smtplib
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Mailing, MailingLog


def send_mailing_now(mailing: Mailing):
    """Отправляет сообщения всем клиентам рассылки и логирует результат"""
    recipient_list = [client.email for client in mailing.clients.all()]

    if not recipient_list:
        # Если клиентов нет, фиксируем это в логах и выходим
        MailingLog.objects.create(
            status='failure',
            server_response='Ошибка: у рассылки отсутствуют получатели.',
            mailing=mailing
        )
        return 0

    # Переводим рассылку в статус "Запущена"
    mailing.status = 'started'
    mailing.save()

    try:
        # Пробуем отправить письмо
        send_mail(
            subject=mailing.message.subject,
            message=mailing.message.body,
            from_email=getattr(settings, 'EMAIL_HOST_USER', 'noreply@mailflow.ru'),
            recipient_list=recipient_list,
            fail_silently=False,
        )

        # Если всё хорошо — пишем успешный лог
        MailingLog.objects.create(
            status='success',
            server_response='Письма успешно отправлены всем получателям.',
            mailing=mailing
        )

        # Завершаем рассылку
        mailing.status = 'completed'

    except (smtplib.SMTPException, Exception) as error:
        # Если сервер упал или почта не существует — ловим ошибку
        MailingLog.objects.create(
            status='failure',
            server_response=f'Ошибка отправки: {str(error)}',
            mailing=mailing
        )

        # Оставляем статус "Создана", чтобы её можно было перезапустить позже
        mailing.status = 'created'

    finally:
        # В любом случае сохраняем итоговый статус рассылки
        mailing.save()

