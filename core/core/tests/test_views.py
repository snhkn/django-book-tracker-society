from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Profile, Book, UserBook, Note

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.profile = self.user.profile
        self.book = Book.objects.create(title="Dune", author="Frank Herbert")
        self.client.login(username='testuser', password='pass')

    def test_dashboard_post_note(self):
        response = self.client.post(reverse('core:dashboard'), {'content': 'My first note'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.first().user, self.user)


    def test_profile_list_view(self):
        response = self.client.get(reverse('core:profile_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/profile_list.html")

    def test_profile_follow_unfollow(self):
        other_user = User.objects.create_user(username='other', password='pass')
        response = self.client.post(reverse('core:profile', args=[other_user.profile.id]), {'follow': 'follow'})
        self.assertIn(other_user.profile, self.profile.follows.all())
        response = self.client.post(reverse('core:profile', args=[other_user.profile.id]), {'follow': 'unfollow'})
        self.assertNotIn(other_user.profile, self.profile.follows.all())

    def test_add_userbook(self):
        response = self.client.post(reverse('core:add_userbook'), {
            'title': 'Dune',
            'author': 'Frank Herbert',
            'status': 'to_read'
        })
        self.assertRedirects(response, reverse('core:my_books'))
        self.assertEqual(UserBook.objects.count(), 1)

    def test_edit_userbook(self):
        userbook = UserBook.objects.create(user=self.profile, book=self.book, status='to_read')
        response = self.client.post(reverse('core:edit_userbook', args=[userbook.id]), {
            'status': 'finished'
        })
        self.assertRedirects(response, reverse('core:profile', args=[self.profile.id]))
        userbook.refresh_from_db()
        self.assertEqual(userbook.status, 'finished')

    def test_delete_userbook(self):
        userbook = UserBook.objects.create(user=self.profile, book=self.book, status='reading')
        response = self.client.post(reverse('core:delete_userbook', args=[userbook.id]))
        self.assertRedirects(response, reverse('core:profile', args=[self.profile.id]))
        self.assertFalse(UserBook.objects.filter(id=userbook.id).exists())

    def test_filtered_books_view(self):
        UserBook.objects.create(user=self.profile, book=self.book, status='reading')
        response = self.client.get(reverse('core:filtered_books', args=['reading']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dune")

    def test_sign_up_view(self):
        response = self.client.post(reverse('core:sign_up'), {
            'username': 'newuser',
            'password1': 'newuserstrongpass1',
            'password2': 'newuserstrongpass1',
        })
        self.assertEqual(User.objects.filter(username='newuser').exists(), True)
        self.assertRedirects(response, reverse('core:dashboard'))

