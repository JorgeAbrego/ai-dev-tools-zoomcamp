from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import Todo
from .forms import TodoForm


class TodoModelTest(TestCase):
    """Test cases for the Todo model."""
    
    def setUp(self):
        """Set up test data."""
        self.todo = Todo.objects.create(
            title="Test TODO",
            description="Test description",
            due_date=date.today() + timedelta(days=7),
            is_resolved=False
        )
    
    def test_todo_creation(self):
        """Test that a TODO can be created."""
        self.assertEqual(self.todo.title, "Test TODO")
        self.assertEqual(self.todo.description, "Test description")
        self.assertFalse(self.todo.is_resolved)
        self.assertIsNotNone(self.todo.created_at)
        self.assertIsNotNone(self.todo.updated_at)
    
    def test_todo_str_method(self):
        """Test the string representation of a TODO."""
        self.assertEqual(str(self.todo), "Test TODO")
    
    def test_is_overdue_false_for_future_date(self):
        """Test that a TODO with future due date is not overdue."""
        self.assertFalse(self.todo.is_overdue)
    
    def test_is_overdue_true_for_past_date(self):
        """Test that a TODO with past due date is overdue."""
        self.todo.due_date = date.today() - timedelta(days=1)
        self.todo.save()
        self.assertTrue(self.todo.is_overdue)
    
    def test_is_overdue_false_when_resolved(self):
        """Test that resolved TODOs are not marked as overdue."""
        self.todo.due_date = date.today() - timedelta(days=1)
        self.todo.is_resolved = True
        self.todo.save()
        self.assertFalse(self.todo.is_overdue)
    
    def test_is_overdue_false_when_no_due_date(self):
        """Test that TODOs without due date are not overdue."""
        self.todo.due_date = None
        self.todo.save()
        self.assertFalse(self.todo.is_overdue)
    
    def test_todo_ordering(self):
        """Test that TODOs are ordered by creation date (newest first)."""
        todo1 = Todo.objects.create(title="First TODO")
        todo2 = Todo.objects.create(title="Second TODO")
        todos = Todo.objects.all()
        self.assertEqual(todos[0], todo2)
        self.assertEqual(todos[1], todo1)


class TodoFormTest(TestCase):
    """Test cases for the TodoForm."""
    
    def test_valid_form(self):
        """Test that a valid form passes validation."""
        form_data = {
            'title': 'Test TODO',
            'description': 'Test description',
            'due_date': date.today() + timedelta(days=7),
            'is_resolved': False
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_without_title(self):
        """Test that form is invalid without a title."""
        form_data = {
            'description': 'Test description',
            'due_date': date.today(),
            'is_resolved': False
        }
        form = TodoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_form_with_optional_fields_empty(self):
        """Test that form is valid with only required fields."""
        form_data = {
            'title': 'Test TODO',
            'description': '',
            'due_date': None,
            'is_resolved': False
        }
        form = TodoForm(data=form_data)
        self.assertTrue(form.is_valid())


class TodoListViewTest(TestCase):
    """Test cases for the TodoListView."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.url = reverse('todo_list')
        
        # Create test TODOs
        self.todo1 = Todo.objects.create(
            title="Active TODO",
            description="This is active",
            is_resolved=False
        )
        self.todo2 = Todo.objects.create(
            title="Completed TODO",
            description="This is completed",
            is_resolved=True
        )
    
    def test_list_view_status_code(self):
        """Test that the list view returns 200 status code."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_list_view_uses_correct_template(self):
        """Test that the list view uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'todos/todo_list.html')
    
    def test_list_view_shows_all_todos(self):
        """Test that all TODOs are displayed by default."""
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['todos']), 2)
    
    def test_list_view_filter_resolved(self):
        """Test filtering for resolved TODOs."""
        response = self.client.get(self.url + '?filter=resolved')
        self.assertEqual(len(response.context['todos']), 1)
        self.assertEqual(response.context['todos'][0], self.todo2)
    
    def test_list_view_filter_unresolved(self):
        """Test filtering for unresolved TODOs."""
        response = self.client.get(self.url + '?filter=unresolved')
        self.assertEqual(len(response.context['todos']), 1)
        self.assertEqual(response.context['todos'][0], self.todo1)


class TodoCreateViewTest(TestCase):
    """Test cases for the TodoCreateView."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('todo_create')
    
    def test_create_view_status_code(self):
        """Test that the create view returns 200 status code."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_create_view_uses_correct_template(self):
        """Test that the create view uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'todos/todo_form.html')
    
    def test_create_todo_post(self):
        """Test creating a TODO via POST request."""
        initial_count = Todo.objects.count()
        response = self.client.post(self.url, {
            'title': 'New TODO',
            'description': 'New description',
            'due_date': date.today() + timedelta(days=7),
            'is_resolved': False
        })
        self.assertEqual(Todo.objects.count(), initial_count + 1)
        self.assertRedirects(response, reverse('todo_list'))
        
        # Verify the TODO was created correctly
        new_todo = Todo.objects.latest('created_at')
        self.assertEqual(new_todo.title, 'New TODO')
        self.assertEqual(new_todo.description, 'New description')


class TodoUpdateViewTest(TestCase):
    """Test cases for the TodoUpdateView."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.todo = Todo.objects.create(
            title="Original Title",
            description="Original description",
            is_resolved=False
        )
        self.url = reverse('todo_update', kwargs={'pk': self.todo.pk})
    
    def test_update_view_status_code(self):
        """Test that the update view returns 200 status code."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_update_view_uses_correct_template(self):
        """Test that the update view uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'todos/todo_form.html')
    
    def test_update_todo_post(self):
        """Test updating a TODO via POST request."""
        response = self.client.post(self.url, {
            'title': 'Updated Title',
            'description': 'Updated description',
            'is_resolved': True
        })
        self.assertRedirects(response, reverse('todo_list'))
        
        # Verify the TODO was updated
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Title')
        self.assertEqual(self.todo.description, 'Updated description')
        self.assertTrue(self.todo.is_resolved)


class TodoDeleteViewTest(TestCase):
    """Test cases for the TodoDeleteView."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.todo = Todo.objects.create(
            title="TODO to Delete",
            description="This will be deleted"
        )
        self.url = reverse('todo_delete', kwargs={'pk': self.todo.pk})
    
    def test_delete_view_status_code(self):
        """Test that the delete view returns 200 status code."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_view_uses_correct_template(self):
        """Test that the delete view uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'todos/todo_confirm_delete.html')
    
    def test_delete_todo_post(self):
        """Test deleting a TODO via POST request."""
        initial_count = Todo.objects.count()
        response = self.client.post(self.url)
        self.assertEqual(Todo.objects.count(), initial_count - 1)
        self.assertRedirects(response, reverse('todo_list'))
        
        # Verify the TODO was deleted
        with self.assertRaises(Todo.DoesNotExist):
            Todo.objects.get(pk=self.todo.pk)


class TodoToggleResolvedTest(TestCase):
    """Test cases for the toggle_resolved view."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.todo = Todo.objects.create(
            title="TODO to Toggle",
            description="This will be toggled",
            is_resolved=False
        )
        self.url = reverse('todo_toggle', kwargs={'pk': self.todo.pk})
    
    def test_toggle_resolved_from_false_to_true(self):
        """Test toggling a TODO from unresolved to resolved."""
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('todo_list'))
        
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_resolved)
    
    def test_toggle_resolved_from_true_to_false(self):
        """Test toggling a TODO from resolved to unresolved."""
        self.todo.is_resolved = True
        self.todo.save()
        
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('todo_list'))
        
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.is_resolved)
    
    def test_toggle_nonexistent_todo(self):
        """Test toggling a nonexistent TODO returns 404."""
        url = reverse('todo_toggle', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TodoIntegrationTest(TestCase):
    """Integration tests for the complete TODO workflow."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_complete_todo_workflow(self):
        """Test the complete workflow: create, view, update, toggle, delete."""
        # 1. Create a TODO
        create_response = self.client.post(reverse('todo_create'), {
            'title': 'Integration Test TODO',
            'description': 'Testing complete workflow',
            'due_date': date.today() + timedelta(days=5),
            'is_resolved': False
        })
        self.assertEqual(create_response.status_code, 302)
        
        # Get the created TODO
        todo = Todo.objects.get(title='Integration Test TODO')
        
        # 2. View the TODO in the list
        list_response = self.client.get(reverse('todo_list'))
        self.assertContains(list_response, 'Integration Test TODO')
        
        # 3. Update the TODO
        update_response = self.client.post(
            reverse('todo_update', kwargs={'pk': todo.pk}),
            {
                'title': 'Updated Integration Test TODO',
                'description': 'Updated description',
                'is_resolved': False
            }
        )
        self.assertEqual(update_response.status_code, 302)
        todo.refresh_from_db()
        self.assertEqual(todo.title, 'Updated Integration Test TODO')
        
        # 4. Toggle resolved status
        toggle_response = self.client.get(
            reverse('todo_toggle', kwargs={'pk': todo.pk})
        )
        self.assertEqual(toggle_response.status_code, 302)
        todo.refresh_from_db()
        self.assertTrue(todo.is_resolved)
        
        # 5. Delete the TODO
        delete_response = self.client.post(
            reverse('todo_delete', kwargs={'pk': todo.pk})
        )
        self.assertEqual(delete_response.status_code, 302)
        self.assertEqual(Todo.objects.filter(pk=todo.pk).count(), 0)
