from django.db import models
from django.utils import timezone


class Todo(models.Model):
    """Model representing a TODO item."""
    
    title = models.CharField(max_length=200, help_text="Enter the TODO title")
    description = models.TextField(blank=True, help_text="Enter a detailed description")
    due_date = models.DateField(null=True, blank=True, help_text="Set a due date")
    is_resolved = models.BooleanField(default=False, help_text="Mark as resolved")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'TODO'
        verbose_name_plural = 'TODOs'
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        """Check if the TODO is overdue."""
        if self.due_date and not self.is_resolved:
            return self.due_date < timezone.now().date()
        return False
