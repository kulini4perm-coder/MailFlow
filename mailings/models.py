from django.db import models
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

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка №{self.id} — {self.message.subject[:20]}... ({self.get_status_display()})"

