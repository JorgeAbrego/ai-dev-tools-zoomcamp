from django.contrib import admin
from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    """Admin configuration for Todo model."""
    
    list_display = ['title', 'due_date', 'is_resolved', 'created_at', 'updated_at']
    list_filter = ['is_resolved', 'due_date', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Status & Dates', {
            'fields': ('is_resolved', 'due_date')
        }),
    )
