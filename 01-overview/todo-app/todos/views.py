from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from .models import Todo
from .forms import TodoForm


class TodoListView(ListView):
    """View to display all TODOs."""
    model = Todo
    template_name = 'todos/todo_list.html'
    context_object_name = 'todos'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filter_type = self.request.GET.get('filter', 'all')
        
        if filter_type == 'resolved':
            queryset = queryset.filter(is_resolved=True)
        elif filter_type == 'unresolved':
            queryset = queryset.filter(is_resolved=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'all')
        return context


class TodoCreateView(CreateView):
    """View to create a new TODO."""
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todo_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context


class TodoUpdateView(UpdateView):
    """View to update an existing TODO."""
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todo_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context


class TodoDeleteView(DeleteView):
    """View to delete a TODO."""
    model = Todo
    template_name = 'todos/todo_confirm_delete.html'
    success_url = reverse_lazy('todo_list')


def toggle_resolved(request, pk):
    """Toggle the resolved status of a TODO."""
    todo = get_object_or_404(Todo, pk=pk)
    todo.is_resolved = not todo.is_resolved
    todo.save()
    return HttpResponseRedirect(reverse_lazy('todo_list'))
