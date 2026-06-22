from django.db import models
from django.conf import settings
from clients.models import Client
from messages_app.models import Message


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    start_date = models.DateTimeField(verbose_name="Дата и время первой отправки")
    end_date = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name="Статус")

    # Внешний ключ на модель сообщения
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение", related_name="mailings")

    # Связь «многие ко многим» с получателями
    clients = models.ManyToManyField(Client, verbose_name="Получатели", related_name="mailings")

    # Привязка к создателю рассылки
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец", blank=True,
                              null=True)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка №{self.id} — {self.message.subject[:20]}... ({self.get_status_display()})"


class MailingLog(models.Model):
    """Модель попытки рассылки"""
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failure', 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ почтового сервера")

    # Внешний ключ на модель Рассылки
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка", related_name="logs")

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ['-attempt_time']  # Последние логи всегда вверху

    def __str__(self):
        return f"Лог №{self.id} для Рассылки №{self.mailing_id} ({self.get_status_display()})"

