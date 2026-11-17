from django import forms
from Shared_models.models import Application, CustomUser, Application_category


class ApplicationCreationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('name', 'description', 'category', 'priority')

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введіть назву заявки'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Опишіть вашу проблему...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.role != CustomUser.Role.MANAGER:
            if 'priority' in self.fields:
                del self.fields['priority']

    def save(self, commit=True, creator=None):
        application = super().save(commit=False)

        if creator:
            application.creator = creator

        if not application.pk:
            application.status = Application.Status.NEW

        if commit:
            application.save()
        return application

class ApplicationCategoryForm(forms.ModelForm):
    class Meta:
        model = Application_category
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть назву нової категорії...'
            }),
        }