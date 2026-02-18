from django import forms

from app_accounts.models import User
from app_projects.models import Project

INPUT_CSS = (
    'w-full px-3 py-2 border border-gray-300 rounded-lg text-sm '
    'text-gray-900 placeholder-gray-400 focus:outline-none '
    'focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 '
    'transition-colors duration-200'
)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CSS,
                'placeholder': 'Nome do projeto (ex: ERP Legacy, Novo Site)',
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CSS,
                'placeholder': 'Descrição do projeto...',
                'rows': 3,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500',
            }),
        }
        labels = {
            'name': 'Nome do Projeto',
            'description': 'Descrição',
            'is_active': 'Projeto Ativo',
        }


class ProjectAddMemberForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Usuário',
        widget=forms.Select(attrs={'class': INPUT_CSS}),
        empty_label='Selecione um usuário',
    )

    def __init__(self, *args, project_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project_instance:
            self.fields['user'].queryset = User.objects.exclude(
                projects=project_instance,
            ).order_by('first_name')
