from django import forms

from app_accounts.models import User
from app_teams.models import Team

INPUT_CSS = (
    'w-full px-3 py-2 border border-gray-300 rounded-lg text-sm '
    'text-gray-900 placeholder-gray-400 focus:outline-none '
    'focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 '
    'transition-colors duration-200'
)


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': INPUT_CSS,
            'placeholder': 'seu@email.com',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CSS,
            'placeholder': '••••••••',
        }),
    )


class UserCreateForm(forms.Form):
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': (
                'block w-full pl-10 pr-4 py-3 bg-white/50 border '
                'border-slate-200 rounded-xl text-slate-800 font-medium '
                'placeholder-slate-400 focus:outline-none focus:ring-4 '
                'focus:ring-indigo-500/10 focus:border-indigo-500 focus:bg-white '
                'hover:bg-white hover:border-slate-300 '
                'transition-all duration-300 shadow-sm'
            ),
            'placeholder': 'Ex: João',
        }),
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': (
                'block w-full pl-10 pr-4 py-3 bg-white/50 border '
                'border-slate-200 rounded-xl text-slate-800 font-medium '
                'placeholder-slate-400 focus:outline-none focus:ring-4 '
                'focus:ring-indigo-500/10 focus:border-indigo-500 focus:bg-white '
                'hover:bg-white hover:border-slate-300 '
                'transition-all duration-300 shadow-sm'
            ),
            'placeholder': 'Ex: Silva',
        }),
    )
    email = forms.EmailField(
        label='E-mail Corporativo',
        widget=forms.EmailInput(attrs={
            'class': (
                'block w-full pl-10 pr-4 py-3 bg-white/50 border '
                'border-slate-200 rounded-xl text-slate-800 font-medium '
                'placeholder-slate-400 focus:outline-none focus:ring-4 '
                'focus:ring-indigo-500/10 focus:border-indigo-500 focus:bg-white '
                'hover:bg-white hover:border-slate-300 '
                'transition-all duration-300 shadow-sm'
            ),
            'placeholder': 'usuario@empresa.com',
        }),
    )
    password = forms.CharField(
        label='Senha Temporária',
        widget=forms.PasswordInput(attrs={
            'class': (
                'block w-full pl-10 pr-10 py-3 bg-white/50 border '
                'border-slate-200 rounded-xl text-slate-800 font-medium '
                'placeholder-slate-400 focus:outline-none focus:ring-4 '
                'focus:ring-indigo-500/10 focus:border-indigo-500 focus:bg-white '
                'hover:bg-white hover:border-slate-300 '
                'transition-all duration-300 shadow-sm'
            ),
            'placeholder': '••••••••',
            'id': 'password',  # Explicit ID for JS toggle
        }),
    )
    role = forms.ChoiceField(
        label='Perfil de Acesso',
        choices=User.Role.choices,
        widget=forms.Select(attrs={
            'class': (
                'appearance-none block w-full pl-10 pr-8 py-3 bg-white/50 '
                'border border-slate-200 rounded-xl text-slate-800 font-medium '
                'focus:outline-none focus:ring-4 focus:ring-indigo-500/10 '
                'focus:border-indigo-500 focus:bg-white '
                'hover:bg-white hover:border-slate-300 '
                'transition-all duration-300 shadow-sm cursor-pointer'
            ),
        }),
    )
    team = forms.ModelChoiceField(
        label='Atribuir a Time',
        queryset=Team.objects.all(),
        required=False,
        empty_label='Nenhum (atribuir depois)',
        widget=forms.Select(attrs={
            'class': (
                'appearance-none block w-full pl-10 pr-8 py-3 bg-white/50 '
                'border border-slate-200 rounded-xl text-slate-800 font-medium '
                'focus:outline-none focus:ring-4 focus:ring-indigo-500/10 '
                'focus:border-indigo-500 focus:bg-white '
                'hover:bg-white hover:border-slate-300 '
                'transition-all duration-300 shadow-sm cursor-pointer'
            ),
        }),
    )


    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Já existe um usuário com este e-mail.',
            )
        return email


class UserEditForm(forms.Form):
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        widget=forms.TextInput(attrs={'class': INPUT_CSS}),
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        widget=forms.TextInput(attrs={'class': INPUT_CSS}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': INPUT_CSS}),
    )
    password = forms.CharField(
        label='Nova Senha',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CSS,
            'placeholder': 'Deixe em branco para manter a atual',
        }),
    )
    role = forms.ChoiceField(
        label='Perfil',
        choices=User.Role.choices,
        widget=forms.Select(attrs={'class': INPUT_CSS}),
    )
    is_active = forms.BooleanField(
        label='Ativo',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-indigo-600 border-gray-300 '
                     'rounded focus:ring-indigo-500',
        }),
    )
    team = forms.ModelChoiceField(
        label='Time',
        queryset=Team.objects.all(),
        required=False,
        empty_label='Nenhum',
        widget=forms.Select(attrs={'class': INPUT_CSS}),
    )

    def __init__(self, *args, user_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_instance = user_instance

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = User.objects.filter(email=email)
        if self.user_instance:
            qs = qs.exclude(pk=self.user_instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                'Já existe um usuário com este e-mail.',
            )
        return email

