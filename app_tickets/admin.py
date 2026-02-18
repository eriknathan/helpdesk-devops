from django.contrib import admin

from app_tickets.models import AuditLog, Comment, Ticket


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['author', 'created_at']


class AuditLogInline(admin.TabularInline):
    model = AuditLog
    extra = 0
    readonly_fields = ['changed_by', 'changed_by_name', 'old_status', 'new_status', 'reason', 'created_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'priority', 'created_by', 'assigned_team', 'assigned_agent', 'created_at']
    list_filter = ['status', 'priority', 'assigned_team', 'is_escalated']
    search_fields = ['title', 'description', 'created_by__email']
    raw_id_fields = ['created_by', 'assigned_agent']
    readonly_fields = ['created_at', 'updated_at', 'first_response_at', 'resolved_at', 'closed_at', 'rt_breached_at']
    inlines = [CommentInline, AuditLogInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'created_at']
    list_filter = ['created_at']
    raw_id_fields = ['ticket', 'author']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'changed_by_name', 'old_status', 'new_status', 'created_at']
    list_filter = ['new_status', 'created_at']
    raw_id_fields = ['ticket', 'changed_by']
    readonly_fields = ['created_at']
