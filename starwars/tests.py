import datetime
from unittest.mock import Mock
from unittest.mock import patch

from django.test import TestCase

from starwars import views
from starwars.models import Collection


class FetchCollectionViewTests(TestCase):
    def setUp(self):
        self.instance = views.FetchCollectionView()

    def test_write_metadata_to_db(self):
        self.instance.filename = 'dummy-filename'
        self.instance.write_metadata_to_db()
        collection = Collection.objects.first()

        self.assertIsNotNone(collection)
        self.assertEqual('dummy-filename', collection.filename)

    @patch('requests.get')
    def test_page_numbers(self, mocked_get):
        mocked_get.return_value = Mock(ok=True)
        mocked_get.return_value.json.return_value = {'count': 82}

        page_numbers = self.instance.page_numbers()

        self.assertEqual(
            range(1, 10),
            page_numbers,
        )

    def test_convert_to_date(self):
        raw_date = '2014-12-20T21:17:56.891000Z'

        self.assertEqual(
            '2014-12-20',
            self.instance.convert_to_date(raw_date),
        )

