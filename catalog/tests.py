from django.test import Client, TestCase


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
    def test_allauth_pages_use_library_layout(self):
        for path in ('/accounts/login/', '/accounts/signup/', '/accounts/password/reset/'):
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Local Library')
