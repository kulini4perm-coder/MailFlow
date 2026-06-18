from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'phone_number', 'country', 'avatar')

class UserProfileForm(UserChangeForm):
    password = None  # Исключаем редактирование пароля из этой формы

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'country', 'avatar')
