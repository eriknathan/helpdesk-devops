from django.urls import path

from app_accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path(
        'users/',
        views.AdminUserListView.as_view(),
        name='user_list',
    ),
    path(
        'users/create/',
        views.AdminUserCreateView.as_view(),
        name='user_create',
    ),
    path(
        'users/<int:pk>/',
        views.AdminUserDetailView.as_view(),
        name='user_detail',
    ),
    path(
        'users/<int:pk>/edit/',
        views.AdminUserEditView.as_view(),
        name='user_edit',
    ),
    path(
        'users/<int:pk>/delete/',
        views.AdminUserDeleteView.as_view(),
        name='user_delete',
    ),
]
