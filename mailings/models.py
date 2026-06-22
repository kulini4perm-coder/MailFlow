from django.db import models
from django.conf import settings
from django.utils import timezone
from clients.models import Client
from messages_app.models import Message


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name="Статус")

    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение", related_name="mailings")
    recipients = models.ManyToManyField(Client, verbose_name="Получатели",
                                        related_name="mailings")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец", blank=True,
                              null=True)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def update_status(self):
        """Динамический пересчет и сохранение статуса рассылки на основе текущего времени"""
        now = timezone.now()
        new_status = self.status

        if now < self.start_time:
            new_status = 'created'
        elif self.start_time <= now <= self.end_time:
            new_status = 'started'
        elif now > self.end_time:
            new_status = 'completed'

        # Если вычисленный статус отличается от текущего в БД — обновляем его
        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def __str__(self):
        return f"Рассылка №{self.id} ({self.get_status_display()})"


class MailingLog(models.Model):
    """Модель попытки рассылки"""
    STATUS_CHOICES = [('success', 'Успешно'), ('failure', 'Не успешно')]
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ сервера")
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка", related_name="logs")

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ['-attempt_time']
