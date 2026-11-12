from django import forms
from Shared_models.models import Application


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

    def save(self, commit=True, creator=None):
        application = super().save(commit=False)

        if creator:
            application.creator = creator

        application.status = Application.Status.NEW

        if commit:
            application.save()
        return application