from bs4 import BeautifulSoup
import requests
from db.doc import Seller
from datetime import datetime


class AutoRiaAuto:
    def __init__(self, bs_post, saller, url):
        self.bs_post = bs_post
        self.saller = saller
        self.post_url = url
        self.start()

    def strip_price(self, price: str):
        bad_simbol = ['$', ' ']
        if 'грн' in price:
            price = price.replace(' грн', '')
            price = {'uk': int(price)}
        elif '$' in price:
            price = price.replace(' $', '')
            price = {'usd': int(price)} 


        return int(price)

    def get_sub_auto_info(self, key_word):
        auto_info = self.bs_post.find('div', {'id': 'description_v3'})
        return auto_info.find('span', string=key_word).find_next_sibling().text

    def strip_type_auto(self, type_auto: str):
        if type_auto.find('•'):
            type_auto = type_auto[:type_auto.find('•')]
        return type_auto

    def strip_engine(self, engine: str):
        fuel_type = None
        if engine.rfind('•') != -1:
            fuel_type = engine[engine.rfind('•') + 2:]
        try:
            engine_capacity = float(engine[:engine.find('л')])
        except ValueError:
            engine_capacity = float(0)
        return engine_capacity, fuel_type

    def strip_duration(self, duration: str):
        if not duration:
            return 0
        return int(duration.replace(' тыс. км', '') + '000')

    def start(self):
        header = self.bs_post.find('div', {'id': 'heading-cars'})
        mark = header.find('span', {'itemprop': 'brand'}).text
        model = header.find('span', {'itemprop': 'name'}).text
        year = int(header.find('h1', 'head').text[-4:])
        price = self.strip_price(self.bs_post.find('div', {'class': 'price_value'}).find('strong').text)
        image = self.bs_post.find('div', 'carousel-inner').find_all('div')[0].find('img')['src']
        autoria_link = self.post_url
        location = self.saller.location


        driving_type = self.get_sub_auto_info('Коробка передач')
        type_auto = self.strip_type_auto(self.bs_post.find('div', {'id': 'description_v3'}).find_all('dd')[0].text)
        engine_capacity, fuel_type = self.strip_engine(self.get_sub_auto_info('Двигатель'))

        duration = self.strip_duration(self.get_sub_auto_info('Пробег'))

        print(f'<mark={mark}, model={model}, year={year}, image={image}, price={price}, autoria_link={autoria_link}, location={location}, driving_type={driving_type}, type_auto={type_auto}, engine_capacity={engine_capacity}, fuel_type={fuel_type}, duration={duration}>')


class AutoRiaSaller:

    def __init__(self, bs_saller):
        self.bs_saller = bs_saller
        self.start()

    def strip_phone_number(self, phone: str):
        simbols = ['(', ')', ' ', ]
        for simbol in simbols:
            phone = phone.replace(simbol, '')
        return phone

    def find_saller(self, saller) -> object:
        for phone in saller.numbers_phones:
            old_saller = Seller.objects.filter(numbers_phones__contains=phone).first()
            if old_saller:
                return old_saller
        saller.save()
        return saller

    def start(self):
        location = self.bs_saller.find('ul', 'checked-list').find('div').text
        name = self.bs_saller.find('div', 'seller_info_area').find('h4').text
        phones = []
        for phone in self.bs_saller.find_all('div', 'phones_item'):
            span = phone.find('span')

            phones.append(self.strip_phone_number(span['data-phone-number']))
        saller = Seller(name=name, location=location, numbers_phones=phones)
        self.saller = self.find_saller(saller)


class AutoRia:
    page_count = 0
    soup = None

    def start(self):
        if not self.soup:
            loc_soup = BeautifulSoup(requests.get('https://auto.ria.com/legkovie/').content, 'html.parser')
        else:
            loc_soup = self.base_page_pars()
        self.page_count += 1
        for i in loc_soup.findAll('section', 'ticket-item'):
            self.pars_post(i('a')[1]['href'])

    def pars_post(self, url: str):
        loc_soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        saller_obj = AutoRiaSaller(loc_soup.find('section', {'id': 'userInfoBlock'}))
        post = AutoRiaAuto(loc_soup, saller_obj.saller, url)

    def base_page_pars(self):
        self.soup = BeautifulSoup(requests.get(f'https://auto.ria.com/legkovie/page={self.page_count}').content,
                                  'html.parser')
