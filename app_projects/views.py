from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, DetailView

from app_accounts.models import User
from app_accounts.views import AdminRequiredMixin
from app_projects.forms import ProjectForm, ProjectAddMemberForm
from app_projects.models import Project


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Project.objects.all().order_by('name')
        return user.projects.all().order_by('name')


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Project.objects.all()
        return user.projects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.members.all().order_by('first_name')
        return context


# Admin Views

class AdminProjectListView(AdminRequiredMixin, ListView):
    model = Project
    template_name = 'projects/admin_list.html'
    context_object_name = 'projects'
    paginate_by = 20
    ordering = ['name']

    def get_queryset(self):
        return super().get_queryset().prefetch_related('members')


class AdminProjectCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = ProjectForm()
        return render(request, 'projects/admin_form.html', {'form': form, 'title': 'Novo Projeto'})

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Projeto "{project.name}" criado com sucesso!')
            return redirect('projects:admin_detail', pk=project.pk)
        return render(request, 'projects/admin_form.html', {'form': form, 'title': 'Novo Projeto'})


class AdminProjectDetailView(AdminRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.members.all().order_by('first_name')
        context['add_member_form'] = ProjectAddMemberForm(project_instance=self.object)
        context['is_admin_view'] = True
        return context


class AdminProjectEditView(AdminRequiredMixin, View):
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectForm(instance=project)
        return render(request, 'projects/admin_form.html', {'form': form, 'title': f'Editar {project.name}'})

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projeto atualizado com sucesso!')
            return redirect('projects:admin_detail', pk=project.pk)
        return render(request, 'projects/admin_form.html', {'form': form, 'title': f'Editar {project.name}'})


class AdminProjectDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.tickets.exists():
            messages.error(request, 'Não é possível excluir este projeto pois existem chamados vinculados. Desative-o em vez disso.')
            return redirect('projects:admin_detail', pk=pk)
            
        name = project.name
        project.delete()
        messages.success(request, f'Projeto "{name}" excluído com sucesso!')
        return redirect('projects:admin_list')


class ProjectMemberAddView(AdminRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectAddMemberForm(request.POST, project_instance=project)
        if form.is_valid():
            user = form.cleaned_data['user']
            project.members.add(user)
            messages.success(request, f'{user.full_name} adicionado ao projeto!')
        else:
            messages.error(request, 'Erro ao adicionar membro.')
        return redirect('projects:admin_detail', pk=pk)


class ProjectMemberRemoveView(AdminRequiredMixin, View):
    def post(self, request, pk, user_id):
        project = get_object_or_404(Project, pk=pk)
        user = get_object_or_404(User, pk=user_id)
        project.members.remove(user)
        messages.success(request, f'{user.full_name} removido do projeto.')
        return redirect('projects:admin_detail', pk=pk)
