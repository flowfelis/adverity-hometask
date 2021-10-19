import http
import os
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
            self.instance._fetch_homeworld('dummy_planet_url'),
        )

    @patch('starwars.views.FetchCollectionView._fetch_from_api_with_thread')
    @patch('starwars.views.FetchCollectionView._transform_and_write_to_csv')
    @patch('starwars.views.FetchCollectionView._write_metadata_to_db')
    def test_fetching(
            self,
            mocked_write_metadata_to_db,
            mocked_transform_and_write_to_csv,
            mocked_fetch_from_api_thread_wrapper,
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

    @patch('requests.get')
    def test_fetch_from_api(self, mocked_get):
        mocked_get.return_value = Mock(ok=True)
        mocked_get.return_value.json.return_value = {'results': [{'name': 'Luke Skywalker'}]}

        self.assertEqual(
            [{'name': 'Luke Skywalker'}],
            self.instance._fetch_from_api('dummy_page_number'),
        )

    @patch('starwars.views.FetchCollectionView._fetch_homeworld_with_thread')
    @patch('starwars.views.FetchCollectionView._convert_to_date')
    def test_transform_and_write_to_csv(
            self,
            mocked_convert_to_date,
            mocked_fetch_homeworld_with_thread,
    ):
        mocked_convert_to_date.return_value = '2020-12-20'
        self.instance.all_characters = [
            {'name': 'Luke Skywalker', 'height': '172', 'mass': '77', 'hair_color': 'blond', 'skin_color': 'fair',
             'eye_color': 'blue', 'birth_year': '19BBY', 'gender': 'male',
             'homeworld': 'https://swapi.dev/api/planets/1/',
             'films': ['https://swapi.dev/api/films/1/', 'https://swapi.dev/api/films/2/',
                       'https://swapi.dev/api/films/3/', 'https://swapi.dev/api/films/6/'], 'species': [],
             'vehicles': ['https://swapi.dev/api/vehicles/14/', 'https://swapi.dev/api/vehicles/30/'],
             'starships': ['https://swapi.dev/api/starships/12/', 'https://swapi.dev/api/starships/22/'],
             'created': '2014-12-09T13:50:51.644000Z', 'edited': '2014-12-20T21:17:56.891000Z',
             'url': 'https://swapi.dev/api/people/1/'}
        ]
        self.instance.resolved_homeworld = ['Naboo']
        self.instance._transform_and_write_to_csv()

        test_filepath = f'files/{self.instance.filename}'
        self.assertTrue(
            os.path.isfile(test_filepath)
        )

        with open(test_filepath) as test_file:
            self.assertEqual(
                'name,height,mass,hair_color,skin_color,eye_color,birth_year,gender,homeworld,date\n'
                'Luke Skywalker,172,77,blond,fair,blue,19BBY,male,Naboo,2020-12-20\n',
                test_file.read()
            )

        os.remove(test_filepath)
