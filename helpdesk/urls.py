from django.contrib import admin
from django.urls import include, path

from app_tickets.dashboard import DashboardView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),
    path('accounts/', include('app_accounts.urls')),
    path('teams/', include('app_teams.urls')),
    path('tickets/', include('app_tickets.urls')),
    path('projects/', include('app_projects.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
