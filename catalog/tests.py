from datetime import date, timedelta

from django.contrib.auth.models import Permission, User
from django.test import Client, TestCase

from .models import Book, BookInstance


class HomePageSessionTests(TestCase):
    def test_home_page_counts_visits_per_session(self):
        client = Client()

        first_response = client.get('/catalog/')
        second_response = client.get('/catalog/')

        self.assertContains(first_response, 'You have visited this page 1 time.')
        self.assertContains(second_response, 'You have visited this page 2 times.')
        self.assertEqual(client.session['num_visits'], 2)

    def test_visit_count_is_isolated_between_clients(self):
        first_client = Client()
        second_client = Client()

        first_client.get('/catalog/')
        second_response = second_client.get('/catalog/')

        self.assertContains(second_response, 'You have visited this page 1 time.')


class AuthenticationPageTests(TestCase):
    def test_login_link_preserves_current_page(self):
        response = self.client.get('/catalog/books/')

        self.assertContains(
            response,
            'href="/accounts/login/?next=/catalog/books/"',
        )

    def test_allauth_pages_use_library_layout(self):
        for path in ('/accounts/login/', '/accounts/signup/', '/accounts/password/reset/'):
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Local Library')


class BorrowedBooksTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='password123',
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='password123',
        )
        self.book = Book.objects.first()
        self.second_book = Book.objects.exclude(pk=self.book.pk).first()

    def test_my_borrowed_requires_login(self):
        response = self.client.get('/catalog/mybooks/')

        self.assertRedirects(
            response,
            '/accounts/login/?next=/catalog/mybooks/',
        )

    def test_my_borrowed_lists_only_current_users_loans_in_due_order(self):
        later = BookInstance.objects.create(
            book=self.book,
            imprint='Test',
            status='o',
            borrower=self.user,
            due_back=date.today() + timedelta(days=5),
        )
        earlier = BookInstance.objects.create(
            book=self.second_book,
            imprint='Test',
            status='o',
            borrower=self.user,
            due_back=date.today() + timedelta(days=1),
        )
        BookInstance.objects.create(
            book=self.book,
            imprint='Test',
            status='a',
            borrower=self.user,
            due_back=date.today(),
        )
        BookInstance.objects.create(
            book=self.book,
            imprint='Test',
            status='o',
            borrower=self.other_user,
            due_back=date.today(),
        )
        self.client.force_login(self.user)

        response = self.client.get('/catalog/mybooks/')

        self.assertEqual(
            list(response.context['bookinstance_list']),
            [earlier, later],
        )
        self.assertContains(response, self.book.title)
        self.assertContains(response, self.second_book.title)

    def test_is_overdue_only_when_due_date_is_in_the_past(self):
        overdue = BookInstance(
            book=self.book,
            imprint='Test',
            due_back=date.today() - timedelta(days=1),
        )
        due_today = BookInstance(
            book=self.book,
            imprint='Test',
            due_back=date.today(),
        )
        no_due_date = BookInstance(book=self.book, imprint='Test')

        self.assertTrue(overdue.is_overdue)
        self.assertFalse(due_today.is_overdue)
        self.assertFalse(no_due_date.is_overdue)

    def test_all_borrowed_requires_permission(self):
        self.client.force_login(self.user)
        response = self.client.get('/catalog/allborrowed/')

        self.assertEqual(response.status_code, 403)

        permission = Permission.objects.get(
            codename='can_mark_returned',
            content_type__app_label='catalog',
        )
        self.user.user_permissions.add(permission)
        response = self.client.get('/catalog/allborrowed/')

        self.assertEqual(response.status_code, 200)
