#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import Amsterdam Maps Spots

Usage:
    api.py [-vqh] [FILE]

Arguments:
  FILE     input json file

Options:
  -h --help
  -v --verbose      verbose mode
  -q --quiet        quiet mode
"""

from __future__ import unicode_literals, print_function
from docopt import docopt
import requests
import json

__version__ = "0.1"
__author__ = "Ashutosh Bandiwdekar"
__license__ = "MIT"


class Importer:
    HOST = 'http://127.0.0.1:8000/api'
    SESSION = None
    SPORT_MAPPING = {
        'FITNESS': '7d5cac64-e9aa-4889-9f3c-803bcc93462c',
        'BEACHVOLLEY': '672e593a-ac57-432a-b718-63d26074db1c',
        'BASKETBAL': '0619c38d-4b21-4663-ba23-b49f682f50a2',
        'VOETBAL': '2e9c614d-632f-4386-a9f5-0d514cb56c15',
        'JEUDEBOULES': '327bee89-789c-4e18-9a50-1f01c2d36a2f',
        'SKATE': '3662531a-957c-4eef-974e-7d4a09d428ea',
        'TENNIS': '8ef143ce-22d5-4155-9e3a-8d2b5d5fdd5c',
        'OVERIG': '512a417f-f8fd-4637-b1ed-860747c60799'
    }

    def __init__(self, filename):
        self.filename = filename
        self.requests = requests.Session()

    def login(self):
        params = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'changeme'
        }
        response = self.requests.post('{}/auth/login/'.format(self.HOST), data=params)

        json_response = response.json()

        csrf_token = response.cookies['csrftoken']
        jwt_token = json_response['token']

        print('JWT TOKEN: {}'.format(jwt_token))
        print('CSRF TOKEN: {}'.format(csrf_token))

        self.requests.headers.update({
            'Authorization': 'JWT {}'.format(jwt_token),
            'X-CSRFToken': '{}'.format(csrf_token)
        })

        return json_response

    @staticmethod
    def _get_spot_attribute(spot, attribute_name):
        for data in spot['attributes']:
            if data['attribute_name'] == attribute_name:
                return data['value']
        return ''

    def _get_sport_uuid(self, sport):
        return self.SPORT_MAPPING[sport]

    def create_spot(self, spot):
        # TODO: Make this interactive by retreving data from the api


        data = {
            'name': spot['label'].title(),
            'owner': 'Gementee Amsterdam',
            'description': self._get_spot_attribute(spot, 'Omschrijving'),
            'homepage_url': 'https://www.amsterdam.nl/'
        }
        # {'FITNESS', 'BEACHVOLLEY', 'BASKETBAL', 'VOETBAL', 'JEUDEBOULES', 'SKATE', 'TENNIS', 'OVERIG'}
        # {'Sportvoorziening': {'Beachvolley', 'Skate', 'Basketbal', 'Tennis', 'Fitness / Bootcamp', 'Overig',
        # 'Jeu de boules', 'Voetbal'}, 'Locatie': {'Park', 'Sportpark', 'Dak sporthal', 'Straat', 'Speeltuin',
        # 'Plantsoen', 'Plein', 'Sportveld', 'Schoolplein'}, 'Omheining': {'Gedeeltelijk', 'Hekwerk', 'Kooi',
        # 'Hekwerk laag', 'Kooi gesloten', 'Ballenvangers', 'Veldafscheiding', 'Kooi open', 'Geen'},
        # 'Ondergrond': {'Stoeptegels', 'Asfalt', 'Klinkers', 'Onverhard', 'Tegels', 'Gras', 'Zand', 'Kunstgras',
        # 'Beton'}, 'Verlichting': {'Ja', 'Nee'}}
        pass

    def start_import(self):
        login_response = self.login()

        with open('sportyscraper/spots.json', encoding='utf-8') as data_file:
            data = json.loads(data_file.read())

            # sports = set()
            # all_attributes = {}
            counter = 0
            for spot in data:
                if counter == 0:
                    spot_params = {
                        'name': spot['label'].title(),
                        'address': {
                            'lat': str(spot['lat']),
                            'lng': str(spot['lng'])
                        },
                        'owner': 'Geemente Amsterdam',
                        'description': self._get_spot_attribute(spot, 'Omschrijving'),
                        'homepage_url': 'https://www.amsterdam.nl'
                    }
                    print('Authorization: {}'.format(self.requests.headers.get('Authorization', None)))
                    print('X-CSRFToken: {}'.format(self.requests.headers.get('X-CSRFToken', None)))
                    spot_response = self.requests.post('{}/spots/'.format(self.HOST), data=spot_params)
                    spot_details = spot_response.json()

                    sport_params = {
                        'uuid': self._get_sport_uuid(spot['sport'])
                    }
                    spot_sport_response = self.requests.post('{}/spots/{}/sports/'.format(self.HOST,
                                                                                          str(spot_details['uuid'])),
                                                             json=sport_params)

                # sports.add(sport['sport'])
                # for attribute in sport['attributes']:
                #     if attribute['attribute_name'] not in ['Omschrijving', 'Oppervlak']:
                #         all_attributes.setdefault(attribute['attribute_name'], set()).add(attribute['value'])


if __name__ == '__main__':
    arguments = docopt(__doc__, version=__version__)
    print(arguments)
    importer = Importer(arguments['FILE'])
    importer.start_import()
