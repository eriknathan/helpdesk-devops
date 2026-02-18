from django.contrib import admin

from app_teams.models import Team, TeamMember


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    raw_id_fields = ['user']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'member_count', 'created_at']
    list_filter = ['level']
    search_fields = ['name']
    inlines = [TeamMemberInline]

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = 'Membros'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'created_at']
    list_filter = ['team']
    raw_id_fields = ['user']
