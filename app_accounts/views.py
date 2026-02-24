from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from app_accounts.forms import LoginForm, UserCreateForm, UserEditForm
from app_accounts.models import User


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(request, 'user') and request.user.is_authenticated:
            if not request.user.is_admin:
                messages.error(
                    request, 'Acesso restrito a administradores.',
                )
                return redirect('/')
        return response


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'E-mail ou senha inválidos.')
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        projects = request.user.projects.filter(is_active=True)
        return render(
            request,
            'accounts/profile.html',
            {'projects': projects},
        )


class AdminUserListView(AdminRequiredMixin, View):
    def get(self, request):
        users = User.objects.prefetch_related(
            'projects',
        ).order_by('-created_at')
        return render(
            request,
            'accounts/user_list.html',
            {'users': users},
        )


class AdminUserCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = UserCreateForm()
        return render(
            request, 'accounts/user_create.html', {'form': form},
        )

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role=form.cleaned_data['role'],
            )
            project = form.cleaned_data.get('project')
            if project:
                project.members.add(user)
            messages.success(
                request,
                f'Usuário {user.full_name} criado com sucesso!',
            )
            return redirect('accounts:user_list')
        return render(
            request, 'accounts/user_create.html', {'form': form},
        )


class AdminUserDetailView(AdminRequiredMixin, View):
    def get(self, request, pk):
        target_user = get_object_or_404(
            User.objects.prefetch_related('projects'),
            pk=pk,
        )
        return render(
            request,
            'accounts/user_detail.html',
            {'target_user': target_user},
        )


class AdminUserEditView(AdminRequiredMixin, View):
    @staticmethod
    def _get_current_project(target_user):
        return target_user.projects.first()

    def get(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        form = UserEditForm(
            initial={
                'first_name': target_user.first_name,
                'last_name': target_user.last_name,
                'email': target_user.email,
                'role': target_user.role,
                'is_active': target_user.is_active,
                'project': self._get_current_project(target_user),
            },
            user_instance=target_user,
        )
        return render(
            request,
            'accounts/user_edit.html',
            {'form': form, 'target_user': target_user},
        )

    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        form = UserEditForm(
            request.POST,
            user_instance=target_user,
        )
        if form.is_valid():
            target_user.first_name = form.cleaned_data['first_name']
            target_user.last_name = form.cleaned_data['last_name']
            target_user.email = form.cleaned_data['email']
            target_user.role = form.cleaned_data['role']
            target_user.is_active = form.cleaned_data['is_active']
            password = form.cleaned_data.get('password')
            if password:
                target_user.set_password(password)
            target_user.save()

            project = form.cleaned_data.get('project')
            target_user.projects.clear()
            if project:
                project.members.add(target_user)

            messages.success(
                request,
                f'Usuário {target_user.full_name} atualizado!',
            )
            return redirect(
                'accounts:user_detail', pk=target_user.pk,
            )
        return render(
            request,
            'accounts/user_edit.html',
            {'form': form, 'target_user': target_user},
        )


class AdminUserDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        if target_user.pk == request.user.pk:
            messages.error(
                request, 'Você não pode excluir a si mesmo.',
            )
            return redirect('accounts:user_list')
        name = target_user.full_name
        target_user.delete()
        messages.success(
            request,
            f'Usuário {name} excluído com sucesso!',
        )
        return redirect('accounts:user_list')
