from django.urls import path

from app_teams import views

app_name = 'teams'

urlpatterns = [
    # Public/User views
    path('', views.TeamListView.as_view(), name='list'),
    path('<int:pk>/', views.TeamDetailView.as_view(), name='detail'),

    # Admin views
    path('admin/', views.AdminTeamListView.as_view(), name='admin_list'),
    path('admin/create/', views.AdminTeamCreateView.as_view(), name='admin_create'),
    path('admin/<int:pk>/', views.AdminTeamDetailView.as_view(), name='admin_detail'),
    path('admin/<int:pk>/edit/', views.AdminTeamEditView.as_view(), name='admin_edit'),
    path('admin/<int:pk>/delete/', views.AdminTeamDeleteView.as_view(), name='admin_delete'),
    path('admin/<int:pk>/members/add/', views.TeamMemberAddView.as_view(), name='member_add'),
    path(
        'admin/<int:pk>/members/<int:user_id>/remove/',
        views.TeamMemberRemoveView.as_view(),
        name='member_remove',
    ),
]
