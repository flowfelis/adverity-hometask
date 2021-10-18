import datetime
import uuid
from concurrent.futures import ThreadPoolExecutor

import petl as etl
import requests
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView
from django.views.generic import ListView

from starwars.models import Collection

DOWNLOAD_DIRECTORY = 'files'
URL = 'https://swapi.dev/api/people'
ITEM_PER_PAGE = 10


class CollectionListView(ListView):
    http_method_names = ['get']
    model = Collection


class CollectionDetailView(DetailView):
    http_method_names = ['get', 'post']
    model = Collection

    def get_from_file(self, context):
        """return headers and values from csv file"""
        file_location = f'{DOWNLOAD_DIRECTORY}/{context.get("collection").filename}'
        table = list(etl.fromcsv(file_location))
        return table[0], table[1:], table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        headers, values, _ = self.get_from_file(context)

        next_page_number = int(self.request.GET.get('page') or 0) + 1
        rows_per_page = next_page_number * ITEM_PER_PAGE
        has_next = True
        total_item = len(values)
        total_page_number = total_item // ITEM_PER_PAGE \
            if total_item % ITEM_PER_PAGE == 0 \
            else total_item // ITEM_PER_PAGE + 1
        if next_page_number >= total_page_number:
            has_next = False

        context['headers'] = headers
        context['headers_for_value_count'] = headers
        context['values'] = values[:rows_per_page]
        context['has_next'] = has_next
        context['next_page_number'] = next_page_number

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        headers, _, table = self.get_from_file(context)

        # filter out csrf_token from request POST body
        checked_headers = [header for header in request.POST.keys() if header != 'csrfmiddlewaretoken']

        try:
            values_count = etl.valuecounter(table, *checked_headers)
        except AssertionError:
            # All headers are unchecked, so show all headers
            return HttpResponseRedirect(reverse('collection-detail', args=[kwargs['pk']]))

        # If only one header is checked, encapsulate in a list
        values = [[val] if type(val) == str else val for val in values_count.keys()]

        value_count_table = [checked_headers] + values
        value_count_table = etl.addcolumn(value_count_table, 'count', values_count.values())

        context['headers_for_value_count'] = headers
        context['headers'] = value_count_table[0]
        context['values'] = value_count_table[1:]
        context['checked_headers'] = checked_headers

        return self.render_to_response(context=context)


class FetchCollection(View):
    http_method_names = ['get']

    def write_metadata_to_db(self):
        Collection.objects.create(filename=self.filename)

    def page_numbers(self):
        resp = requests.get(URL)
        total_item = resp.json().get('count')
        total_page_number = total_item // ITEM_PER_PAGE \
            if total_item % ITEM_PER_PAGE == 0 \
            else total_item // ITEM_PER_PAGE + 1
        return range(1, total_page_number + 1)

    def convert_to_date(self, raw_date):
        d = datetime.datetime.strptime(raw_date[:raw_date.find('T')], '%Y-%m-%d')
        return str(d.date())

    def fetch_homeworld(self, planet_url):
        resp = requests.get(planet_url)
        data = resp.json()
        return data['name']

    def resolve_homeworld(self, planet_urls):
        with ThreadPoolExecutor() as executor:
            results = executor.map(self.fetch_homeworld, planet_urls)

            self.resolved_homeworld = [result for result in results]

    def get(self, request, *args, **kwargs):
        self.fetch_characters_from_api()
        self.transform_and_write_to_csv()
        self.write_metadata_to_db()
        return HttpResponseRedirect(reverse('collection-list'))

    def fetch_from_api(self, page_number):
        resp = requests.get(f'{URL}/?page={page_number}')
        data = resp.json()
        return data.get('results')

    def fetch_characters_from_api(self):
        self.all_characters = []
        with ThreadPoolExecutor() as executor:
            results = executor.map(self.fetch_from_api, self.page_numbers())

            for result in results:
                self.all_characters.extend(result)

    def transform_and_write_to_csv(self):
        self.filename = f'{str(uuid.uuid4())}.csv'
        file_location = f'{DOWNLOAD_DIRECTORY}/{self.filename}'

        header = [list(self.all_characters[0].keys())]
        values = [list(character.values()) for character in self.all_characters]
        table = header + values

        planet_urls = list(etl.values(table, 'homeworld'))
        self.resolve_homeworld(planet_urls)

        etl.cutout(table, 'homeworld') \
            .addcolumn('homeworld', self.resolved_homeworld, index=8) \
            .addfield('date', lambda row: self.convert_to_date(row['edited'])) \
            .cutout('films', 'species', 'vehicles', 'starships', 'created', 'edited', 'url') \
            .tocsv(file_location)
