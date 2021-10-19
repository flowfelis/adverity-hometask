import http
from unittest.mock import Mock
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from starwars import views
from starwars.models import Collection


class FetchCollectionViewTests(TestCase):
    def setUp(self):
        self.instance = views.FetchCollectionView()

    def test_api(self):
        pass

    def test_write_metadata_to_db(self):
        self.instance.filename = 'dummy-filename'
        self.instance._write_metadata_to_db()
        collection = Collection.objects.first()

        self.assertIsNotNone(collection)
        self.assertEqual('dummy-filename', collection.filename)

    @patch('requests.get')
    def test_page_numbers(self, mocked_get):
        mocked_get.return_value = Mock(ok=True)
        mocked_get.return_value.json.return_value = {'count': 82}

        page_numbers = self.instance._page_numbers()

        self.assertEqual(
            range(1, 10),
            page_numbers,
        )

    def test_convert_to_date(self):
        raw_date = '2014-12-20T21:17:56.891000Z'

        self.assertEqual(
            '2014-12-20',
            self.instance._convert_to_date(raw_date),
        )

    @patch('requests.get')
    def test_fetch_homeworld(self, mocked_get):
        mocked_get.return_value = Mock(ok=True)
        mocked_get.return_value.json.return_value = {'name': 'Naboo'}

        self.assertEqual(
            'Naboo',
            self.instance._fetch_homeworld('planet_url'),
        )

    @patch('starwars.views.FetchCollectionView._fetch_from_api_thread_wrapper')
    @patch('starwars.views.FetchCollectionView._transform_and_write_to_csv')
    @patch('starwars.views.FetchCollectionView._write_metadata_to_db')
    def test_fetching(
            self,
            mocked_fetch_characters_from_api,
            mocked_transform_and_write_to_csv,
            mocked_write_metadata_to_db,
    ):
        resp = self.client.get(reverse('fetch'))
        self.assertEqual(
            http.HTTPStatus.FOUND,
            resp.status_code,
        )
        self.assertEqual(
            '/',
            resp.url,
        )

    # @patch()
    def test_fetch_from_api(self):
        pass
