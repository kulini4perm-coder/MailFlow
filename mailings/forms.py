from django import forms
from django.utils import timezone
from .models import Mailing


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['message', 'recipients', 'start_time', 'end_time']

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        # Если это создание новой рассылки, проверяем, чтобы дата не была в прошлом
        if not self.instance.pk and start_time < timezone.now():
            raise forms.ValidationError("Дата начала рассылки не может быть в прошлом!")
        return start_time

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("Дата окончания рассылки должна быть строго позже даты начала!")
        return cleaned_data
