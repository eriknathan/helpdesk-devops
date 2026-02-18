from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView

from app_accounts.models import User
from app_accounts.views import AdminRequiredMixin
from app_teams.forms import TeamForm, AddMemberForm
from app_teams.models import Team, TeamMember


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'teams/list.html'
    context_object_name = 'teams'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('members__user')
        return queryset


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = 'teams/detail.html'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.members.select_related('user').order_by('user__first_name')
        return context


# Admin Views

class AdminTeamListView(AdminRequiredMixin, ListView):
    model = Team
    template_name = 'teams/admin_list.html'
    context_object_name = 'teams'
    paginate_by = 20
    ordering = ['name']

    def get_queryset(self):
        return super().get_queryset().prefetch_related('members')


class AdminTeamCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = TeamForm()
        return render(request, 'teams/admin_form.html', {'form': form, 'title': 'Novo Time'})

    def post(self, request):
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            messages.success(request, f'Time "{team.name}" criado com sucesso!')
            return redirect('teams:admin_detail', pk=team.pk)
        return render(request, 'teams/admin_form.html', {'form': form, 'title': 'Novo Time'})


class AdminTeamDetailView(AdminRequiredMixin, DetailView):
    model = Team
    template_name = 'teams/detail.html'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.members.select_related('user').order_by('user__first_name')
        context['add_member_form'] = AddMemberForm(team_instance=self.object)
        context['is_admin_view'] = True
        return context


class AdminTeamEditView(AdminRequiredMixin, View):
    def get(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        form = TeamForm(instance=team)
        return render(request, 'teams/admin_form.html', {'form': form, 'title': f'Editar {team.name}'})

    def post(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, 'Time atualizado com sucesso!')
            return redirect('teams:admin_detail', pk=team.pk)
        return render(request, 'teams/admin_form.html', {'form': form, 'title': f'Editar {team.name}'})


class AdminTeamDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        name = team.name
        team.delete()
        messages.success(request, f'Time "{name}" excluído com sucesso!')
        return redirect('teams:admin_list')


class TeamMemberAddView(AdminRequiredMixin, View):
    def post(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        form = AddMemberForm(request.POST, team_instance=team)
        if form.is_valid():
            user = form.cleaned_data['user']
            TeamMember.objects.create(team=team, user=user)
            messages.success(request, f'{user.full_name} adicionado ao time!')
        else:
            messages.error(request, 'Erro ao adicionar membro.')
        return redirect('teams:admin_detail', pk=pk)


class TeamMemberRemoveView(AdminRequiredMixin, View):
    def post(self, request, pk, user_id):
        team = get_object_or_404(Team, pk=pk)
        member = get_object_or_404(TeamMember, team=team, user_id=user_id)
        user_name = member.user.full_name
        member.delete()
        messages.success(request, f'{user_name} removido do time.')
        return redirect('teams:admin_detail', pk=pk)

