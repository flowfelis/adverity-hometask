from django.test import TestCase
from starwars import views
from starwars.models import Collection


class FetchCollectionViewTests(TestCase):
    def test_write_metadata_to_db(self):
        instance = views.FetchCollectionView()
        instance.filename = 'dummy-filename'
        instance.write_metadata_to_db()
        collection = Collection.objects.first()

        self.assertIsNotNone(collection)
        self.assertEqual('dummy-filename', collection.filename)
