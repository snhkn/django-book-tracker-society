from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Profile, Book, UserBook, Feed, Note

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.profile = self.user.profile
        self.book = Book.objects.create(title="1984", author="George Orwell")

    def test_profile_created_on_user_creation(self):
        self.assertIsInstance(self.profile, Profile)
        self.assertEqual(self.profile.user, self.user)

    def test_profile_auto_follows_self(self):
        self.assertIn(self.profile, self.profile.follows.all())

    def test_book_creation(self):
        self.assertEqual(str(self.book), "1984 - George Orwell")

    def test_user_book_status(self):
        user_book = UserBook.objects.create(user=self.profile, book=self.book, status="reading")
        self.assertEqual(str(user_book), "testuser - 1984 (reading)")

    def test_user_book_unique_constraint(self):
        UserBook.objects.create(user=self.profile, book=self.book, status="to_read")
        with self.assertRaises(Exception): # IntegrityError wrapped by Django
            UserBook.objects.create(user=self.profile, book=self.book, status='finished')

    def test_feed_creation(self):
        feed = Feed.objects.create(user=self.user, book=self.book, action='added')
        self.assertEqual(str(feed), "testuser Added to read list 1984")

    def test_note_creation(self):
        note = Note.objects.create(user=self.user, content="Just a short note.")
        self.assertEqual(str(note), "testuser: Just a short note.")