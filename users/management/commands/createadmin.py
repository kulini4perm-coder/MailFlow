from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailings.models import Mailing

class Command(BaseCommand):
    help = 'Создание суперпользователя и группы Менеджеров'

    def handle(self, *args, **options):
        User = get_user_model()

        # Создаем или получаем группу менеджеров
        manager_group, created = Group.objects.get_or_create(name='Менеджеры')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" успешно создана.'))

        # Создаем суперпользователя
        email = 'testadmin@mail.ru'
        if not User.objects.filter(email=email).exists():
            user = User.objects.create(email=email, first_name='Admin', last_name='Adminoff')
            user.is_staff = True
            user.is_superuser = True
            user.set_password('1234')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Успешное создание суперпользователя {user.email}.'))
