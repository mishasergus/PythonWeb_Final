from django.contrib.auth.forms import UserCreationForm
from Shared_models.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = CustomUser.Role.CLIENT

        if commit:
            user.save()
        return user