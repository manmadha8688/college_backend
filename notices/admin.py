from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """Admin interface for Notice model"""
    list_display = ('category', 'title', 'audience', 'priority', 'posted_by', 'created_at')
    list_filter = ('category', 'audience', 'priority', 'created_at')
    search_fields = ('title', 'content', 'category', 'posted_by__email', 'posted_by__first_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'audience', 'title', 'content')
        }),
        ('Dates', {
            'fields': ('date', 'datetime', 'expiry_date')
        }),
        ('Additional', {
            'fields': ('priority', 'posted_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
