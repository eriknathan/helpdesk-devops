from django import forms

from app_accounts.models import User
from app_teams.models import Team

INPUT_CSS = (
    'w-full px-3 py-2 border border-gray-300 rounded-lg text-sm '
    'text-gray-900 placeholder-gray-400 focus:outline-none '
    'focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 '
    'transition-colors duration-200'
)


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description', 'level']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CSS,
                'placeholder': 'Nome do time (ex: DevOps, SRE, Suporte)',
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CSS,
                'placeholder': 'Descrição opcional do time...',
                'rows': 3,
            }),
            'level': forms.Select(attrs={'class': INPUT_CSS}),
        }
        labels = {
            'name': 'Nome do Time',
            'description': 'Descrição',
            'level': 'Nível de Atendimento',
        }


class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Usuário',
        widget=forms.Select(attrs={'class': INPUT_CSS}),
        empty_label='Selecione um usuário',
    )

    def __init__(self, *args, team_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        if team_instance:
            # Exclude users already in the team
            self.fields['user'].queryset = User.objects.exclude(
                team_memberships__team=team_instance,
            ).order_by('first_name')
