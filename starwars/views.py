import requests
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView
from django.views.generic import ListView

from starwars.models import Collection


class CollectionListView(ListView):
    http_method_names = ['get']
    model = Collection


class CollectionDetailView(DetailView):
    http_method_names = ['get']
    model = Collection

    def render_to_response(self, context, **response_kwargs):
        filename = context.get('collection').filename
        # read from csv
        # with open(filename) as f:
        #     pass
        # update context with csv content
        return super().render_to_response(context, **response_kwargs)


class FetchCollection(View):
    http_method_names = ['get']
    URL = 'https://swapi.dev/api/people'
    ITEM_PER_PAGE = 10

    def get(self, request, *args, **kwargs):
        self.fetch_collection()
        return HttpResponseRedirect(reverse('collection-list'))

    def total_page_number(self):
        resp = requests.get(FetchCollection.URL)
        total_item = resp.json().get('count')
        total_page_number = total_item // FetchCollection.ITEM_PER_PAGE \
            if total_item % FetchCollection.ITEM_PER_PAGE == 0 \
            else total_item // FetchCollection.ITEM_PER_PAGE + 1
        return total_page_number

    def fetch_collection(self):
        # there is one extra request being made for only fetching "count" number.
        # but this is preferred for code-readability over performance(because not significant)

        # url = 'https://swapi.dev/api/people'
        # get "count" (total_item)
        # item_per_page = 10
        # total_page_number = count // item_per_page if count % item_per_page == 0 else count // item_per_page + 1
        # for page_number in range(1, total_page_number+1):
        #   self.data = fetch from url + '/?page=page_number' (Using threading)
        #   self.save()
        pass

    def save(self):
        # transformed_data = self.transform_data(self.data)
        # self.save_to_csv(transformed_data)
        # metadata = fetch metadata
        # self.save_to_db(metadata)
        pass

    def transform_data(self, data):
        pass

    def save_to_csv(self, data):
        pass

    def save_to_db(self, data):
        pass
