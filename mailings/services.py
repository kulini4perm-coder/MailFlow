import smtplib
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Mailing, MailingLog


def send_mailing_now(mailing: Mailing):
    """Отправляет сообщения с жесткой валидацией разрешенного интервала времени"""
    now = timezone.now()

    # Проверка временного интервала перед отправкой
    if not (mailing.start_time <= now <= mailing.end_time):
        error_msg = f"Ошибка запуска: текущее время {now.strftime('%d.%m.%Y %H:%M')} не входит в интервал рассылки."

        # Фиксируем попытку как неуспешную из-за нарушения регламента времени
        MailingLog.objects.create(
            status='failure',
            server_response=error_msg,
            mailing=mailing
        )
        return False, error_msg

    # Определение получателей
    recipient_list = [client.email for client in mailing.recipients.all()]

    if not recipient_list:
        error_msg = "Ошибка запуска: у рассылки отсутствуют получатели."
        MailingLog.objects.create(
            status='failure',
            server_response=error_msg,
            mailing=mailing
        )
        return False, error_msg

    # Переводим в статус "Запущена"
    mailing.status = 'started'
    mailing.save()

    try:
        # Отправка писем с помощью send_mail()
        send_mail(
            subject=mailing.message.subject,
            message=mailing.message.body,
            from_email=getattr(settings, 'EMAIL_HOST_USER', 'noreply@mailflow.ru'),
            recipient_list=recipient_list,
            fail_silently=False,
        )

        # Создается запись со статусом 'Успешно'
        MailingLog.objects.create(
            status='success',
            server_response='Письма успешно отправлены всем получателям.',
            mailing=mailing
        )
        mailing.status = 'completed'
        mailing.save()
        return True, "Рассылка успешно выполнена!"

    except (smtplib.SMTPException, Exception) as error:
        # Создается запись со статусом 'Не успешно' и текстом ошибки
        server_error = f"Ошибка почтового сервера: {str(error)}"
        MailingLog.objects.create(
            status='failure',
            server_response=server_error,
            mailing=mailing
        )
        # Возвращаем статус в исходный, чтобы можно было исправить настройки
        mailing.status = 'created'
        mailing.save()
        return False, server_error
