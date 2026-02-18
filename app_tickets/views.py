from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from app_tickets.forms import (
    AssignForm,
    CATEGORY_FORMS,
    CATEGORY_TITLES,
    CommentForm,
    TicketCreateForm,
    TransitionForm,
)
from app_tickets.models import AuditLog, Comment, Ticket
from app_tickets.services import (
    VALID_TRANSITIONS,
    TransitionError,
    transition_ticket,
)
from app_tickets.sla import check_sla_status, is_rt_breached


class TicketSelectCategoryView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_admin:
            messages.error(
                request,
                'Apenas clientes podem abrir chamados.',
            )
            return redirect('tickets:list')
        return render(
            request, 'tickets/select_category.html',
        )


class TicketCreateView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            messages.error(
                request,
                'Apenas clientes podem abrir chamados.',
            )
            return redirect('tickets:list')
        return super().dispatch(request, *args, **kwargs)

    def _get_category(self):
        return (
            self.request.POST.get('category')
            or self.request.GET.get('category', 'OTHER')
        )

    def get(self, request):
        category = self._get_category()
        FormClass = CATEGORY_FORMS.get(category)

        if FormClass:
            form = FormClass(user=request.user)
            title = CATEGORY_TITLES.get(category, '')
            return render(
                request,
                'tickets/create_category.html',
                {
                    'form': form,
                    'category': category,
                    'category_title': title,
                },
            )

        form = TicketCreateForm(
            user=request.user,
            initial={'category': 'OTHER'},
        )
        return render(
            request, 'tickets/create.html',
            {'form': form},
        )

    def post(self, request):
        category = self._get_category()
        FormClass = CATEGORY_FORMS.get(category)

        if FormClass:
            form = FormClass(
                request.POST, request.FILES,
                user=request.user,
            )
            if form.is_valid():
                title = CATEGORY_TITLES.get(category, '')
                description = form.compose_description()
                ticket = Ticket.objects.create(
                    title=title,
                    description=description,
                    category=category,
                    project=form.cleaned_data['project'],
                    priority=form.cleaned_data[
                        'priority'
                    ],
                    attachment=form.cleaned_data.get(
                        'attachment',
                    ),
                    created_by=request.user,
                    status=Ticket.Status.OPEN,
                )
                self._create_audit_logs(
                    ticket, request.user,
                )
                messages.success(
                    request,
                    f'Chamado #{ticket.pk} criado '
                    f'com sucesso.',
                )
                return redirect('tickets:list')
            title = CATEGORY_TITLES.get(category, '')
            return render(
                request,
                'tickets/create_category.html',
                {
                    'form': form,
                    'category': category,
                    'category_title': title,
                },
            )

        form = TicketCreateForm(
            request.POST, request.FILES,
            user=request.user,
        )
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.status = Ticket.Status.OPEN
            ticket.category = 'OTHER'
            ticket.save()
            self._create_audit_logs(ticket, request.user)
            messages.success(
                request,
                f'Chamado #{ticket.pk} criado com sucesso.',
            )
            return redirect('tickets:list')
        return render(
            request, 'tickets/create.html',
            {'form': form},
        )

    def _create_audit_logs(self, ticket, user):
        AuditLog.objects.create(
            ticket=ticket,
            changed_by=user,
            changed_by_name=(
                user.full_name or user.email
            ),
            old_status='',
            new_status=Ticket.Status.OPEN,
            reason='Chamado criado pelo cliente.',
        )
        ticket.status = Ticket.Status.TRIAGE
        ticket.save(update_fields=['status'])
        AuditLog.objects.create(
            ticket=ticket,
            changed_by=None,
            changed_by_name='SYSTEM',
            old_status=Ticket.Status.OPEN,
            new_status=Ticket.Status.TRIAGE,
            reason='Transição automática para triagem.',
        )


class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        qs = Ticket.objects.select_related(
            'created_by', 'assigned_team', 'assigned_agent',
            'project',
        )
        if self.request.user.is_customer:
            qs = qs.filter(created_by=self.request.user)

        q = self.request.GET.get('q', '').strip()
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
            )

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        priority = self.request.GET.get('priority')
        if priority:
            qs = qs.filter(priority=priority)

        project_id = self.request.GET.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)

        date_from = self.request.GET.get('date_from')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        date_to = self.request.GET.get('date_to')
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        return qs

    def get_context_data(self, **kwargs):
        from app_projects.models import Project
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = Ticket.Status.choices
        ctx['priority_choices'] = Ticket.Priority.choices
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['current_priority'] = self.request.GET.get('priority', '')
        ctx['current_q'] = self.request.GET.get('q', '')
        ctx['current_project'] = self.request.GET.get('project', '')
        ctx['current_date_from'] = self.request.GET.get(
            'date_from', '',
        )
        ctx['current_date_to'] = self.request.GET.get(
            'date_to', '',
        )
        user = self.request.user
        if user.is_admin:
            ctx['projects'] = Project.objects.filter(
                is_active=True,
            )
        else:
            ctx['projects'] = user.projects.filter(
                is_active=True,
            )
        return ctx


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'tickets/detail.html'
    context_object_name = 'ticket'

    def get_queryset(self):
        qs = Ticket.objects.select_related(
            'created_by', 'assigned_team', 'assigned_agent',
        )
        if self.request.user.is_customer:
            qs = qs.filter(created_by=self.request.user)
        return qs

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        self._check_escalation(obj)
        return obj

    def _check_escalation(self, ticket):
        if (
            not ticket.is_escalated
            and ticket.status not in (
                Ticket.Status.RESOLVED,
                Ticket.Status.CLOSED,
            )
            and is_rt_breached(ticket)
        ):
            from app_teams.models import Team
            n2 = Team.objects.filter(level=Team.Level.N2).first()
            ticket.rt_breached_at = timezone.now()
            ticket.is_escalated = True
            if n2:
                ticket.assigned_team = n2
            ticket.save(update_fields=[
                'rt_breached_at', 'is_escalated',
                'assigned_team',
            ])
            AuditLog.objects.create(
                ticket=ticket,
                changed_by=None,
                changed_by_name='SYSTEM',
                old_status=ticket.status,
                new_status=ticket.status,
                reason='RT_BREACHED_ESCALATED',
            )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ticket = self.object
        user = self.request.user

        ctx['comments'] = (
            ticket.comments.select_related('author')
            .order_by('created_at')
        )
        ctx['audit_logs'] = ticket.audit_logs.order_by('created_at')
        ctx['comment_form'] = CommentForm()
        ctx['sla'] = self._build_sla_ctx()

        allowed = self._get_allowed_transitions(user)
        if allowed:
            ctx['transition_form'] = TransitionForm(
                allowed_transitions=allowed,
            )
        ctx['allowed_transitions'] = allowed

        if user.is_admin:
            ctx['assign_form'] = AssignForm(instance=ticket)

        return ctx

    def _get_allowed_transitions(self, user):
        status = self.object.status
        targets = VALID_TRANSITIONS.get(status, [])
        if not targets:
            return []

        allowed = []
        for t in targets:
            is_reopen = (
                status == Ticket.Status.RESOLVED
                and t == Ticket.Status.IN_PROGRESS
            )
            if is_reopen or user.is_admin:
                allowed.append(t)
        return allowed

    def _build_sla_ctx(self):
        ticket = self.object
        info = check_sla_status(ticket)
        fmt = self._fmt

        frt_secs = (
            int(info['frt'].total_seconds()) if info['frt']
            else int(
                (timezone.now() - ticket.created_at)
                .total_seconds()
            )
        )
        rt_secs = int(info['rt'].total_seconds())

        return {
            'frt_display': fmt(frt_secs),
            'frt_pending': info['frt_pending'],
            'frt_breached': info['frt_breached'],
            'frt_target': fmt(
                int(info['frt_target'].total_seconds()),
            ),
            'rt_display': fmt(rt_secs),
            'rt_pending': (
                ticket.status != Ticket.Status.CLOSED
                and ticket.resolved_at is None
            ),
            'rt_breached': info['rt_breached'],
            'rt_target': fmt(
                int(info['rt_target'].total_seconds()),
            ),
            'is_escalated': ticket.is_escalated,
        }

    @staticmethod
    def _fmt(seconds):
        if seconds < 60:
            return f'{seconds}s'
        elif seconds < 3600:
            return f'{seconds // 60}min'
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f'{h}h {m}min'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = Comment.objects.create(
                ticket=self.object,
                author=request.user,
                content=form.cleaned_data['content'],
            )

            if (
                request.user.is_admin
                and self.object.first_response_at is None
            ):
                self.object.first_response_at = comment.created_at
                self.object.save(
                    update_fields=['first_response_at'],
                )

            messages.success(request, 'Comentário adicionado.')
            return redirect(
                'tickets:detail', pk=self.object.pk,
            )

        ctx = self.get_context_data()
        ctx['comment_form'] = form
        return self.render_to_response(ctx)


class TicketTransitionView(LoginRequiredMixin, View):

    def post(self, request, pk):
        ticket = Ticket.objects.select_related(
            'assigned_agent',
        ).get(pk=pk)

        new_status = request.POST.get('new_status', '')
        reason = request.POST.get('reason', '')

        try:
            transition_ticket(ticket, new_status, request.user, reason)
            messages.success(
                request,
                f'Status alterado para {ticket.get_status_display()}.',
            )
        except TransitionError as e:
            messages.error(request, str(e))

        return redirect('tickets:detail', pk=pk)


class TicketAssignView(LoginRequiredMixin, View):

    def post(self, request, pk):
        if not request.user.is_admin:
            messages.error(
                request,
                'Apenas administradores podem atribuir chamados.',
            )
            return redirect('tickets:detail', pk=pk)

        ticket = Ticket.objects.get(pk=pk)

        if 'assign_me' in request.POST:
            ticket.assigned_agent = request.user
            ticket.save(update_fields=['assigned_agent'])
            AuditLog.objects.create(
                ticket=ticket,
                changed_by=request.user,
                changed_by_name=(
                    request.user.full_name or request.user.email
                ),
                old_status=ticket.status,
                new_status=ticket.status,
                reason='Atribuição do responsável.',
            )
            messages.success(request, 'Chamado atribuído a você.')
        else:
            form = AssignForm(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
                AuditLog.objects.create(
                    ticket=ticket,
                    changed_by=request.user,
                    changed_by_name=(
                        request.user.full_name
                        or request.user.email
                    ),
                    old_status=ticket.status,
                    new_status=ticket.status,
                    reason='Atribuição de time/responsável.',
                )
                messages.success(
                    request, 'Atribuição atualizada.',
                )
            else:
                messages.error(
                    request, 'Erro ao atualizar atribuição.',
                )

        return redirect('tickets:detail', pk=pk)
