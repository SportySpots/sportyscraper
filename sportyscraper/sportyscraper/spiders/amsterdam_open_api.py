# -*- coding: utf-8 -*-
import scrapy
import json

deLegenda = dict()
deLegenda['SPORT_OPENBAAR_SKATE'] = ['_php/haal_objecten.php?TABEL=SPORT_OPENBAAR&SELECT=SKATE&SELECTIEKOLOM=SELECTIE','SPORT_OPENBAAR','SKATE','SELECTIE','Skate']
deLegenda['SPORT_OPENBAAR_TENNIS'] = ['_php/haal_objecten.php?TABEL=SPORT_OPENBAAR&SELECT=TENNIS&SELECTIEKOLOM=SELECTIE','SPORT_OPENBAAR','TENNIS','SELECTIE','Tennis']
deLegenda['SPORT_OPENBAAR_BASKETBALL'] = ['_php/haal_objecten.php?TABEL=SPORT_OPENBAAR&SELECT=BASKETBAL&SELECTIEKOLOM=SELECTIE','SPORT_OPENBAAR','BASKETBAL','SELECTIE','Basketbal']
deLegenda['SPORT_OPENBAAR_VOETBALL'] = ['_php/haal_objecten.php?TABEL=SPORT_OPENBAAR&SELECT=VOETBAL&SELECTIEKOLOM=SELECTIE','SPORT_OPENBAAR','VOETBAL','SELECTIE','Voetbal']
deLegenda['SPORT_OPENBAAR_JEUDEBOL'] = ['_php/haal_objecten.php?TABEL=SPORT_OPENBAAR&SELECT=JEUDEBOULES&SELECTIEKOLOM=SELECTIE','SPORT_OPENBAAR','JEUDEBOULES','SELECTIE','Jeu de boules']
deLegenda['SPORT_OPENBAAR_FITNESS'] = ['_php/haal_objecten.php?TABEL=SPORT_OPENBAAR&SELECT=FITNESS&SELECTIEKOLOM=SELECTIE','SPORT_OPENBAAR','FITNESS','SELECTIE','Fitness / Bootcamp']
deLegenda['SPORT_OPENBAAR_BEACHVOLLEY'] = ['_php/haal_objecten.php?TABEL=SPORT_OPENBAAR&SELECT=BEACHVOLLEY&SELECTIEKOLOM=SELECTIE','SPORT_OPENBAAR','BEACHVOLLEY','SELECTIE','Beachvolley']
deLegenda['SPORT_OPENBAAR_OVERIG'] = ['_php/haal_objecten.php?TABEL=SPORT_OPENBAAR&SELECT=OVERIG&SELECTIEKOLOM=SELECTIE','SPORT_OPENBAAR','OVERIG','SELECTIE','Overig']
# deLegenda['FUNCTIEKAART_S01'] = ['_php/haal_objecten.php?TABEL=FUNCTIEKAART&SELECT=S01&SELECTIEKOLOM=FUNCTIE2_ID','FUNCTIEKAART','S01','FUNCTIE2_ID','Stadion - IJsbaan - Tribunegebouw bij sportbaan']
# deLegenda['FUNCTIEKAART_S02'] = ['_php/haal_objecten.php?TABEL=FUNCTIEKAART&SELECT=S02&SELECTIEKOLOM=FUNCTIE2_ID','FUNCTIEKAART','S02','FUNCTIE2_ID','Zwembad']
# deLegenda['FUNCTIEKAART_S03'] = ['_php/haal_objecten.php?TABEL=FUNCTIEKAART&SELECT=S03&SELECTIEKOLOM=FUNCTIE2_ID','FUNCTIEKAART','S03','FUNCTIE2_ID','Sporthal - Tennishal - Sportzaal - Klimhal']
# deLegenda['FUNCTIEKAART_S04'] = ['_php/haal_objecten.php?TABEL=FUNCTIEKAART&SELECT=S04&SELECTIEKOLOM=FUNCTIE2_ID','FUNCTIEKAART','S04','FUNCTIE2_ID','Sportschool - Fitness - Yogaruimte']
# deLegenda['FUNCTIEKAART_S05'] = ['_php/haal_objecten.php?TABEL=FUNCTIEKAART&SELECT=S05&SELECTIEKOLOM=FUNCTIE2_ID','FUNCTIEKAART','S05','FUNCTIE2_ID','Kleinschalige bebouwing op sportterrein, golfterrein, manege']
# deLegenda['FUNCTIEKAART_S06'] = ['_php/haal_objecten.php?TABEL=FUNCTIEKAART&SELECT=S06&SELECTIEKOLOM=FUNCTIE2_ID','FUNCTIEKAART','S06','FUNCTIE2_ID','Watersportgebouw']
# deLegenda[''] = ['_php/haal_objecten.php?TABEL=HOOFDGROENSTRUCTUUR&SELECT=SPORTPARK&SELECTIEKOLOM=SELECTIE','HOOFDGROENSTRUCTUUR','SPORTPARK','SELECTIE','Sportpark']
# deLegenda[''] = ['_php/haal_objecten.php?TABEL=STADSDELEN_LIJN','STADSDELEN_LIJN','','','STADSDELEN_LIJN']


class Spot(scrapy.Item):
    id = scrapy.Field(serializer=int)
    label = scrapy.Field(serializer=str)
    lat = scrapy.Field()
    lng = scrapy.Field()
    type = scrapy.Field(serializer=str)
    sport = scrapy.Field(serializer=str)
    attributes = scrapy.Field()
    image = scrapy.Field(serializer=str)


class AmsterdamOpenApiSpider(scrapy.Spider):
    name = 'amsterdam_open_api'
    allowed_domains = ['maps.amsterdam.nl']
    # start_urls = ['https://maps.amsterdam.nl/']
    DOMAIN = 'https://maps.amsterdam.nl'

    def parse(self, response):
        pass

    def create_urls(self):
        urls = []
        for key, value in deLegenda.items():
            urls.append('%(domain)s/%(url)s' % {'domain': self.DOMAIN, 'url': value[0]})
        return urls

    def start_requests(self):
        urls = self.create_urls()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_spots)

    def parse_spots(self, response):
        api_response = json.loads(response.body_as_unicode())

        for spot in api_response:
            item = Spot()
            item['id'] = spot['VOLGNR']
            item['label'] = spot['LABEL']
            item['lat'] = spot['LATMAX']
            item['lng'] = spot['LNGMAX']
            item['type'] = spot['TYPE']
            item['sport'] = spot['SELECTIE']

            request = scrapy.Request('https://maps.amsterdam.nl/_php/haal_info.php?VOLGNR=%s&THEMA=sport&TABEL=SPORT_OPENBAAR' % spot['VOLGNR'], callback=self.parse_spot_details)
            request.meta['item'] = item
            yield request

    def parse_spot_details(self, response):
        item = response.meta['item']
        rows = response.css('tr')
        item['attributes'] = list()
        for row in rows:
            field = row.css('td.veld::text').extract()[0]
            if field == '\xa0':
                value = row.css('img::attr(src)').extract()[0]
                item['image'] = value
            else:
                value = row.css('.waarde::text').extract()[0]
                item['attributes'].append({'attribute_name': field, 'value': value})

        yield item
