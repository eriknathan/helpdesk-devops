from django import forms

from app_accounts.models import User
from app_tickets.models import Ticket

TAILWIND_INPUT = (
    'w-full px-3 py-2 border border-gray-300 rounded-lg text-sm '
    'text-gray-900 placeholder-gray-400 focus:outline-none '
    'focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 '
    'transition-colors duration-200'
)

TAILWIND_SELECT = (
    'w-full px-3 py-2 border border-gray-300 rounded-lg text-sm '
    'text-gray-900 focus:outline-none focus:ring-2 '
    'focus:ring-indigo-500 focus:border-indigo-500 '
    'transition-colors duration-200'
)


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'title', 'description', 'project',
            'priority', 'category', 'attachment',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': TAILWIND_INPUT,
                'placeholder': 'Título do chamado',
            }),
            'description': forms.Textarea(attrs={
                'class': TAILWIND_INPUT,
                'placeholder': 'Descreva o problema...',
                'rows': 5,
            }),
            'project': forms.Select(attrs={
                'class': TAILWIND_SELECT,
            }),
            'priority': forms.Select(attrs={
                'class': TAILWIND_SELECT,
            }),
            'category': forms.HiddenInput(),
            'attachment': forms.ClearableFileInput(attrs={
                'class': (
                    'block w-full text-sm text-gray-500 '
                    'file:mr-4 file:py-2 file:px-4 '
                    'file:rounded-lg file:border-0 '
                    'file:text-sm file:font-medium '
                    'file:bg-indigo-50 file:text-indigo-700 '
                    'hover:file:bg-indigo-100'
                ),
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            from app_projects.models import Project
            if user.is_admin:
                qs = Project.objects.filter(is_active=True)
            else:
                qs = user.projects.filter(is_active=True)
            self.fields['project'].queryset = qs
            self.fields['project'].required = True
            self.fields['project'].empty_label = (
                "Selecione um Projeto"
            )

    def compose_description(self):
        """Override in subclasses to build description."""
        return self.cleaned_data.get('description', '')


class _CategoryFormBase(forms.Form):
    """Base mixin for category-specific extra fields."""
    project = forms.ModelChoiceField(
        label='Projeto',
        queryset=None,
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
    )
    priority = forms.ChoiceField(
        label='Prioridade',
        choices=Ticket.Priority.choices,
        initial=Ticket.Priority.P3,
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
    )
    attachment = forms.FileField(
        label='Anexo',
        required=False,
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            from app_projects.models import Project
            if user.is_admin:
                qs = Project.objects.filter(is_active=True)
            else:
                qs = user.projects.filter(is_active=True)
            self.fields['project'].queryset = qs
            self.fields['project'].empty_label = (
                "Selecione um Projeto"
            )


class GitHubRepoForm(_CategoryFormBase):
    repo_name = forms.CharField(
        label='Nome do repositório',
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ex: meu-projeto-api',
        }),
    )
    org_owner = forms.CharField(
        label='Organização / Owner',
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ex: minha-organizacao',
        }),
    )
    visibility = forms.ChoiceField(
        label='Visibilidade',
        choices=[
            ('Privado', 'Privado'),
            ('Público', 'Público'),
        ],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
    )
    repo_description = forms.CharField(
        label='Descrição do repositório',
        widget=forms.Textarea(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Breve descrição do repositório...',
            'rows': 2,
        }),
    )
    template = forms.CharField(
        label='Template (se aplicável)',
        required=False,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ex: template-nodejs',
        }),
    )
    reason = forms.CharField(
        label='Motivo ou justificativa',
        widget=forms.Textarea(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Justifique a necessidade...',
            'rows': 3,
        }),
    )

    def compose_description(self):
        d = self.cleaned_data
        lines = [
            '📦 Solicitação de Novo Repositório no GitHub',
            '',
            f'• Nome do repositório: {d["repo_name"]}',
            f'• Organização/Owner: {d["org_owner"]}',
            f'• Visibilidade: {d["visibility"]}',
            f'• Descrição: {d["repo_description"]}',
        ]
        if d.get('template'):
            lines.append(f'• Template: {d["template"]}')
        lines.append(f'• Justificativa: {d["reason"]}')
        return '\n'.join(lines)


class GitHubUserForm(_CategoryFormBase):
    request_type = forms.ChoiceField(
        label='Tipo de solicitação',
        choices=[
            ('Adicionar', 'Adicionar acesso'),
            ('Remover', 'Remover acesso'),
        ],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
    )
    full_name = forms.CharField(
        label='Nome completo do usuário',
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ex: João da Silva',
        }),
    )
    corporate_email = forms.EmailField(
        label='E-mail corporativo',
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ex: joao@empresa.com',
        }),
    )
    github_username = forms.CharField(
        label='Username do GitHub',
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ex: @joaosilva',
        }),
    )
    repo_links = forms.CharField(
        label='Link(s) do(s) repositório(s)',
        widget=forms.Textarea(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': (
                'Um link por linha...\n'
                'https://github.com/org/repo1\n'
                'https://github.com/org/repo2'
            ),
            'rows': 3,
        }),
    )
    permission_level = forms.ChoiceField(
        label='Nível de permissão',
        choices=[
            ('Read', 'Leitura (Read)'),
            ('Write', 'Escrita (Write)'),
            ('Admin', 'Administrador (Admin)'),
        ],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
    )
    reason = forms.CharField(
        label='Motivo ou justificativa',
        widget=forms.Textarea(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Justifique a necessidade...',
            'rows': 3,
        }),
    )

    def compose_description(self):
        d = self.cleaned_data
        return '\n'.join([
            '👤 Solicitação de Acesso a Repositório GitHub',
            '',
            f'• Tipo: {d["request_type"]}',
            '',
            'Dados do usuário:',
            f'• Nome completo: {d["full_name"]}',
            f'• E-mail corporativo: {d["corporate_email"]}',
            f'• Username GitHub: {d["github_username"]}',
            '',
            'Dados do acesso:',
            f'• Repositório(s): {d["repo_links"]}',
            f'• Permissão: {d["permission_level"]}',
            '',
            f'• Justificativa: {d["reason"]}',
        ])


class ServiceOutageForm(_CategoryFormBase):
    service_name = forms.CharField(
        label='Nome do serviço afetado',
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ex: API de Pagamentos',
        }),
    )
    endpoint = forms.CharField(
        label='URL ou endpoint afetado',
        required=False,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ex: https://api.exemplo.com/v1/pay',
        }),
    )
    outage_start = forms.DateTimeField(
        label='Data e hora do início',
        widget=forms.DateTimeInput(attrs={
            'class': TAILWIND_INPUT,
            'type': 'datetime-local',
        }),
    )
    impact = forms.CharField(
        label='Impacto observado',
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': (
                'ex: erro 500, timeout, lentidão'
            ),
        }),
    )
    environment = forms.ChoiceField(
        label='Ambiente',
        choices=[
            ('Produção', 'Produção'),
            ('Staging', 'Staging'),
            ('Desenvolvimento', 'Desenvolvimento'),
        ],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
    )
    evidence = forms.CharField(
        label='Evidências (prints, logs, etc)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Cole logs ou descreva as evidências...',
            'rows': 3,
        }),
    )
    detailed_description = forms.CharField(
        label='Descrição detalhada do problema',
        widget=forms.Textarea(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Descreva o problema em detalhes...',
            'rows': 4,
        }),
    )

    def compose_description(self):
        d = self.cleaned_data
        lines = [
            '🚨 Reporte de Indisponibilidade de Serviço',
            '',
            f'• Serviço afetado: {d["service_name"]}',
        ]
        if d.get('endpoint'):
            lines.append(f'• Endpoint: {d["endpoint"]}')
        lines += [
            f'• Início: {d["outage_start"]}',
            f'• Impacto: {d["impact"]}',
            f'• Ambiente: {d["environment"]}',
        ]
        if d.get('evidence'):
            lines.append(
                f'• Evidências: {d["evidence"]}'
            )
        lines.append(
            f'\nDescrição: {d["detailed_description"]}'
        )
        return '\n'.join(lines)


class S3BucketForm(_CategoryFormBase):
    bucket_name = forms.CharField(
        label='Nome sugerido para o bucket',
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'ex: meu-projeto-assets',
        }),
    )
    aws_region = forms.ChoiceField(
        label='Região AWS',
        choices=[
            ('sa-east-1', 'São Paulo (sa-east-1)'),
            ('us-east-1', 'N. Virginia (us-east-1)'),
            ('us-west-2', 'Oregon (us-west-2)'),
            ('eu-west-1', 'Irlanda (eu-west-1)'),
        ],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
    )
    purpose = forms.CharField(
        label='Finalidade do bucket',
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': (
                'ex: armazenamento de arquivos, '
                'backups, assets'
            ),
        }),
    )
    public_access = forms.ChoiceField(
        label='Necessita acesso público?',
        choices=[
            ('Não', 'Não'),
            ('Sim', 'Sim'),
        ],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
    )
    policies = forms.CharField(
        label='Políticas especiais',
        required=False,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': (
                'ex: versionamento, lifecycle, '
                'replicação'
            ),
        }),
    )
    reason = forms.CharField(
        label='Motivo ou justificativa',
        widget=forms.Textarea(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Justifique a necessidade...',
            'rows': 3,
        }),
    )

    def compose_description(self):
        d = self.cleaned_data
        lines = [
            '🪣 Solicitação de Criação de Bucket S3',
            '',
            f'• Nome do bucket: {d["bucket_name"]}',
            f'• Região AWS: {d["aws_region"]}',
            f'• Finalidade: {d["purpose"]}',
            f'• Acesso público: {d["public_access"]}',
        ]
        if d.get('policies'):
            lines.append(
                f'• Políticas: {d["policies"]}'
            )
        lines.append(f'• Justificativa: {d["reason"]}')
        return '\n'.join(lines)


CATEGORY_FORMS = {
    'GITHUB_REPO': GitHubRepoForm,
    'GITHUB_USER': GitHubUserForm,
    'SERVICE_OUTAGE': ServiceOutageForm,
    'S3_BUCKET': S3BucketForm,
}

CATEGORY_TITLES = {
    'GITHUB_REPO': 'Novo Repositório no GitHub',
    'GITHUB_USER': (
        'Adicionar usuário em repositório GitHub'
    ),
    'SERVICE_OUTAGE': (
        'Reporte de Indisponibilidade de Serviço'
    ),
    'S3_BUCKET': 'Criação de Bucket S3 para um projeto',
}


class CommentForm(forms.Form):
    content = forms.CharField(
        label='Comentário',
        widget=forms.Textarea(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Escreva seu comentário...',
            'rows': 3,
        }),
    )


class TransitionForm(forms.Form):
    new_status = forms.ChoiceField(
        label='Novo Status',
        choices=[],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
    )
    reason = forms.CharField(
        label='Motivo',
        required=False,
        widget=forms.Textarea(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Informe o motivo (obrigatório para algumas transições)...',
            'rows': 2,
        }),
    )

    def __init__(self, *args, allowed_transitions=None, **kwargs):
        super().__init__(*args, **kwargs)
        if allowed_transitions:
            self.fields['new_status'].choices = [
                (s.value, s.label) for s in allowed_transitions
            ]


class AssignForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['assigned_team', 'assigned_agent']
        widgets = {
            'assigned_team': forms.Select(attrs={
                'class': TAILWIND_SELECT,
            }),
            'assigned_agent': forms.Select(attrs={
                'class': TAILWIND_SELECT,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_agent'].queryset = User.objects.filter(
            role=User.Role.ADMIN,
            is_active=True,
        )
        self.fields['assigned_team'].required = False
        self.fields['assigned_agent'].required = False
