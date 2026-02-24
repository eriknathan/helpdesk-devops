from django import forms

from app_accounts.models import User
from app_projects.models import Project

INPUT_CSS = (
    'block w-full py-3 bg-slate-50 border border-slate-200 '
    'rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none '
    'focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 '
    'transition-all shadow-sm'
)


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': (
                    'block w-full pl-10 pr-4 py-3 bg-slate-50 border '
                    'border-slate-200 rounded-xl text-slate-900 '
                    'placeholder-slate-400 focus:outline-none focus:ring-2 '
                    'focus:ring-violet-500/20 focus:border-violet-500 '
                    'transition-all shadow-sm'
                ),
                'placeholder': 'Ex: Redesign do ERP Legacy',
            }),
            'description': forms.Textarea(attrs={
                'class': (
                    'block w-full pl-10 pr-4 py-3 bg-slate-50 border '
                    'border-slate-200 rounded-xl text-slate-900 '
                    'placeholder-slate-400 focus:outline-none focus:ring-2 '
                    'focus:ring-violet-500/20 focus:border-violet-500 '
                    'transition-all shadow-sm resize-none'
                ),
                'placeholder': (
                    'Descreva brevemente o escopo e os objetivos deste projeto...'
                ),
                'rows': 4,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'sr-only peer',
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
