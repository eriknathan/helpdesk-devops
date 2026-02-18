from django.urls import path

from app_projects import views

app_name = 'projects'

urlpatterns = [
    # Public/User views
    path('', views.ProjectListView.as_view(), name='list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),

    # Admin views
    path('admin/', views.AdminProjectListView.as_view(), name='admin_list'),
    path('admin/create/', views.AdminProjectCreateView.as_view(), name='admin_create'),
    path('admin/<int:pk>/', views.AdminProjectDetailView.as_view(), name='admin_detail'),
    path('admin/<int:pk>/edit/', views.AdminProjectEditView.as_view(), name='admin_edit'),
    path('admin/<int:pk>/delete/', views.AdminProjectDeleteView.as_view(), name='admin_delete'),
    path('admin/<int:pk>/members/add/', views.ProjectMemberAddView.as_view(), name='member_add'),
    path(
        'admin/<int:pk>/members/<int:user_id>/remove/',
        views.ProjectMemberRemoveView.as_view(),
        name='member_remove',
    ),
]
