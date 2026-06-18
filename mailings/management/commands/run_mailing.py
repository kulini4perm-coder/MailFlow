from django.core.management.base import BaseCommand, CommandError
from mailings.models import Mailing
from mailings.services import send_mailing_now


class Command(BaseCommand):
    help = 'Вручную запускает рассылку по её ID через командную строку'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки, которую нужно запустить')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с ID {mailing_id} не найдена.')

        self.stdout.write(self.style.WARNING(f'Запуск рассылки {mailing.id}...'))

        # Вызываем сервис отправки
        sent = send_mailing_now(mailing)

        self.stdout.write(
            self.style.SUCCESS(f'Успешно отправлено писем: {sent}. Статус рассылки: {mailing.get_status_display()}'))
