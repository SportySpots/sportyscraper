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
import googlemaps
from time import sleep
import os

__version__ = "0.1"
__author__ = "Ashutosh Bandiwdekar"
__license__ = "MIT"

gmaps = googlemaps.Client(key="AIzaSyBx6FrEC34yo04MmZtLW78n8Z8xi0GJlCM")


class Importer:
    HOST = "http://127.0.0.1:8000/api"
    SESSION = None
    SPORT_MAPPING = {
        "FITNESS": "7d5cac64-e9aa-4889-9f3c-803bcc93462c",
        "BEACHVOLLEY": "672e593a-ac57-432a-b718-63d26074db1c",
        "BASKETBAL": "0619c38d-4b21-4663-ba23-b49f682f50a2",
        "VOETBAL": "2e9c614d-632f-4386-a9f5-0d514cb56c15",
        "JEUDEBOULES": "327bee89-789c-4e18-9a50-1f01c2d36a2f",
        "SKATE": "3662531a-957c-4eef-974e-7d4a09d428ea",
        "TENNIS": "8ef143ce-22d5-4155-9e3a-8d2b5d5fdd5c",
        "OVERIG": "512a417f-f8fd-4637-b1ed-860747c60799",
    }

    def __init__(self, filename):
        self.filename = filename
        self.requests = requests.Session()

    def login(self):
        params = {
            "username": "admin",
            # 'email': 'admin@sportyspots.com',
            "password": "changeme",
        }
        response = self.requests.post("{}/auth/login/".format(self.HOST), data=params)

        json_response = response.json()
        print(json_response)

        jwt_token = json_response["token"]
        # csrf_token = response.cookies.get('csrftoken', default='')

        self.requests.headers.update(
            {
                "Authorization": "JWT {}".format(jwt_token),
                # 'X-CSRFToken': '{}'.format(csrf_token)
            }
        )

        return json_response

    @staticmethod
    def _get_spot_attribute(spot, attribute_name):
        for data in spot["attributes"]:
            if data["attribute_name"] == attribute_name:
                return data["value"]
        return ""

    # {'FITNESS', 'BEACHVOLLEY', 'BASKETBAL', 'VOETBAL', 'JEUDEBOULES', 'SKATE', 'TENNIS', 'OVERIG'}
    # {'Sportvoorziening': {'Beachvolley', 'Skate', 'Basketbal', 'Tennis', 'Fitness / Bootcamp', 'Overig',
    # 'Jeu de boules', 'Voetbal'}, 'Locatie': {'Park', 'Sportpark', 'Dak sporthal', 'Straat', 'Speeltuin',
    # 'Plantsoen', 'Plein', 'Sportveld', 'Schoolplein'}, 'Omheining': {'Gedeeltelijk', 'Hekwerk', 'Kooi',
    # 'Hekwerk laag', 'Kooi gesloten', 'Ballenvangers', 'Veldafscheiding', 'Kooi open', 'Geen'},
    # 'Ondergrond': {'Stoeptegels', 'Asfalt', 'Klinkers', 'Onverhard', 'Tegels', 'Gras', 'Zand', 'Kunstgras',
    # 'Beton'}, 'Verlichting': {'Ja', 'Nee'}}

    def start_import(self):
        pass
        # TODO: Throw error if login failed
        login_response = self.login()

        with open("sportyscraper/spots.json", encoding="utf-8") as data_file:
            data = json.loads(data_file.read())

            for spot in data:
                # sleep(1)
                # Address
                lat = spot["lat"]
                lng = spot["lng"]
                with open(
                    "files/amsterdam-addresses.json", "r+", encoding="utf-8"
                ) as address_file:
                    spot_address = None
                    # Search for address in pre-computed addresses file
                    for line in address_file:
                        if line:
                            address = json.loads(line)
                            if address["lat"] == str(lat) and address["lng"] == str(
                                lng
                            ):
                                raw_geocode_response = address["raw_data"]
                                spot_address = address["raw_data"][0]
                                break

                    # Reverse geocode if lat,lng wasnt found in the pre-computed addresses file
                    if not spot_address:
                        reverse_geocode_result = gmaps.reverse_geocode((lat, lng))
                        address_file.write(
                            json.dumps(
                                {
                                    "lat": str(lat),
                                    "lng": str(lng),
                                    "raw_data": reverse_geocode_result,
                                }
                            )
                            + "\n"
                        )
                        spot_address = reverse_geocode_result[0]
                        raw_geocode_response = reverse_geocode_result
                        sleep(5)

                spot_params = {
                    "name": spot["label"].title(),
                    "owner": "Geemente Amsterdam",
                    "description": self._get_spot_attribute(spot, "Omschrijving"),
                    "homepage_url": "https://www.amsterdam.nl",
                }

                # create spot
                spot_response = self.requests.post(
                    "{}/spots/".format(self.HOST), data=spot_params
                )
                spot_details = spot_response.json()
                print(spot_response.text)

                # create address
                address_params = {
                    "lat": str(lat),
                    "lng": str(lng),
                    "geocoder_service": "google",
                    "raw_geocoder_response": raw_geocode_response,
                    "formatted_address": spot_address["formatted_address"],
                }
                address_response = self.requests.post(
                    "{}/spots/{}/address/".format(self.HOST, str(spot_details["uuid"])),
                    json=address_params,
                )
                print(address_response.text)

                # associate sport with the spot
                sport_params = {"uuid": self.SPORT_MAPPING[spot["sport"]]}
                # TODO: Log error when response status code is not 201
                sport_response = self.requests.post(
                    "{}/spots/{}/sports/".format(self.HOST, str(spot_details["uuid"])),
                    json=sport_params,
                )
                print(sport_response.text)

                # Download image
                image_url = spot.get("image", None)
                if image_url:
                    filename = image_url.split("/")[-1]
                    file_downloaded = os.path.isfile("files/images/{}".format(filename))

                    if not file_downloaded:
                        r = requests.get(image_url, timeout=5)
                        if r.status_code == 200:
                            with open("files/images/{}".format(filename), "wb+") as f:
                                f.write(r.content)

                    # reconfirm if file was downloaded
                    if os.path.isfile("files/images/{}".format(filename)):
                        files = {
                            "image": open("files/images/{}".format(filename), "rb")
                        }
                        image_response = self.requests.post(
                            "{}/spots/{}/sports/{}/images/".format(
                                self.HOST,
                                str(spot_details["uuid"]),
                                self.SPORT_MAPPING[spot["sport"]],
                            ),
                            files=files,
                        )
                        print(image_response.text)


if __name__ == "__main__":
    arguments = docopt(__doc__, version=__version__)
    importer = Importer(arguments["FILE"])
    importer.start_import()
