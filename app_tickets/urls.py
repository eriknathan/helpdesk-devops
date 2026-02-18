from django.urls import path

from app_tickets import views

app_name = 'tickets'

urlpatterns = [
    path('', views.TicketListView.as_view(), name='list'),
    path(
        'create/select/',
        views.TicketSelectCategoryView.as_view(),
        name='select_category',
    ),
    path('create/', views.TicketCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TicketDetailView.as_view(), name='detail'),
    path(
        '<int:pk>/transition/',
        views.TicketTransitionView.as_view(),
        name='transition',
    ),
    path(
        '<int:pk>/assign/',
        views.TicketAssignView.as_view(),
        name='assign',
    ),
]
