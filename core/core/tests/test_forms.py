from django.test import TestCase
from core.forms import UserBookForm, EditUserBookForm, NoteForm
from core.models import User, Profile, Book, UserBook, Note


class FormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="formuser", password="test")
        self.profile = self.user.profile
        self.book = Book.objects.create(title="test book", author="test author")
        self.user_book = UserBook.objects.create(user=self.profile, book=self.book, status='to_read')

    def test_user_book_form_valid_data(self):
        form_data = {
            'title': '  the alchemist  ',
            'author': ' paulo coelho ',
            'status': 'reading'
        }
        form = UserBookForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'The Alchemist')
        self.assertEqual(form.cleaned_data['author'], 'Paulo Coelho')

    def test_user_book_form_missing_fields(self):
        form = UserBookForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('author', form.errors)
        self.assertIn('status', form.errors)

    def test_edit_user_book_form_valid(self):
        form = EditUserBookForm(instance=self.user_book, data={'status': 'finished'})
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.status, 'finished')

    def test_edit_user_book_form_invalid_status(self):
        form = EditUserBookForm(instance=self.user_book, data={'status': 'invalid'})
        self.assertFalse(form.is_valid())

    def test_note_form_valid(self):
        form_data = {
            'content': ' This is a test note. '
        }
        form = NoteForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['content'], 'This is a test note.')

    def test_note_form_empty(self):
        form = NoteForm(data={'content': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
