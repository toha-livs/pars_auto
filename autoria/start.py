import asyncio
import re
import threading

from bs4 import BeautifulSoup
import requests

from db.doc import Seller, PostAuto
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
            price = price.replace('грн', '')
            price = price.replace(' ', '')
            price = {'uk': int(price)}
        elif '$' in price:
            price = price.replace('$', '')
            price = price.replace(' ', '')
            price = {'usd': int(price)}
        elif '€' in price:
            price = price.replace('€', '')
            price = price.replace(' ', '')
            price = {'eur': int(price)}
        return price

    def get_sub_auto_info(self, key_word):
        auto_info = self.bs_post.find('div', {'id': 'description_v3'})
        if auto_info.find('span', string=key_word) is None:
            return None
        return auto_info.find('span', string=key_word).find_next_sibling().text

    def strip_type_auto(self, type_auto: str):
        if type_auto.find('•'):
            type_auto = type_auto[:type_auto.find('•')]
        return type_auto

    def strip_engine(self, engine: str):
        fuel_type = None
        engine_capacity = None
        try:
            if engine.rfind('•') != -1:
                fuel_type = engine[engine.rfind('•') + 2:]
                engine_capacity = float(engine[:engine.find('л')])
        except ValueError:
            engine_capacity = float(0)
        except AttributeError:
            engine_capacity = float(0)
        return engine_capacity, fuel_type

    def strip_duration(self, duration: str):
        if not duration or duration == 'без пробега':
            return 0
        return int(duration.replace(' тыс. км', '') + '000')

    def has_cyrillic(self, text):
        if re.search('[а-яА-Я]', text):
            text = text[:text.find(re.search('[а-яА-Я]', text).group(0))]
        return text

    def start(self):
        header = self.bs_post.find('div', {'id': 'heading-cars'})
        engine_capacity, fuel_type = self.strip_engine(self.get_sub_auto_info('Двигатель'))
        # print('залупа', self.has_cyrillic(header.find('span', {'itemprop': 'name'}).text))
        # model = self.has_cyrillic(header.find('span', {'itemprop': 'name'}).text)
        data = {
            'mark': header.find('span', {'itemprop': 'brand'}).text,
            'model': self.has_cyrillic(header.find('span', {'itemprop': 'name'}).text),
            'data_created_auto': datetime(int(header.find('h1', 'head').text[-4:]), 1, 1),
            'price': self.strip_price(self.bs_post.find('div', {'class': 'price_value'}).find('strong').text),
            'image': self.bs_post.find('div', 'carousel-inner').find_all('div')[0].find('img')['src'],
            'autoria_link': self.post_url,
            'location': self.saller.location,
            'driving_type': self.get_sub_auto_info('Коробка передач'),
            'type_auto': self.strip_type_auto(
                self.bs_post.find('div', {'id': 'description_v3'}).find_all('dd')[0].text),
            'engine_capacity': engine_capacity,
            'fuel_type': fuel_type,
            'duration': self.strip_duration(self.get_sub_auto_info('Пробег'))
        }
        datetime_now = datetime.now()

        auto = PostAuto(**data)
        by_link = PostAuto.objects.filter(autoria_link=auto.autoria_link).first()
        # by_phone_saller = PostAuto.objects.filter(saller__numbers_phones__contains=auto.saller.numbers_phones[0], mark=).firest()
        if by_link:
            by_link.update(**data)
            by_link.date_updated = datetime_now
            by_link.save()
            print('post by link autoria already exists')
            print(by_link)

        else:
            auto.save()
            print(auto)


class AutoRiaSaller:
    country = (("Ивано-Франковск", "Ивано-Франковская", "Ивано-Франковск",),
              ("Харьков", "Харьковская", "Харьков",),
              ("Хмельницк", "Хмельницкая", "Хмельницк",),
              ("Житомир", "Житомирская", "Житомир",),
              ("Киев", "Киевская", "Киев",),
              ("Винница", "Винницкая", "Винница",),
              ("Днепропетровск", "Днепропетровская", "Днепропетровск",),
              ("Донецк", "Донецкая", "Донецк",),
              ("Луцк", "Волынская", "Луцк",),
              ("Херсон", "Херсонская", "Херсон",),
              ("Запороже", "Запорожская", "Запороже",),
              ("Полтава", "Полтавская", "Полтава",),
              ("Одесса", "Одесская", "Одесса",),
              ("Луганск", "Луганская", "Луганск",),
              ("Николаев", "Николаевская", "Николаев",),
              ("Черкассы", "Черкасская", "Черкассы",),
              ("Львов", "Львовская", "Львов",),
              ("Тернополь", "Тернопольская", "Тернополь",),
              ("Сумы", "Сумская", "Сумы",),
              ("Кропивницкий", "Кропивницкая", "Кропивницкий",),
              ("Закарпатская", "Закарпатье", "Закарпатская",),
              ("Чернигов", "Черниговская", "Чернигов",),
              ("Ужгород", "Ужгород", "Ужгород",),
              ("Черновцы", "Черновицкая", "Черновцы",),
              ("Луганск", "Луганская", "Луганск",),
              ("Ровно", "Ровенская", "Ровно",),)

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

    def clear_location(self, location):
        resp = next(filter(lambda item: item[0] in location or item[1] in location, self.country), ('', '', None))[2]
        return resp

    def start(self):
        location = self.clear_location(self.bs_saller.find('ul', 'checked-list').find('div').text)
        print(location)
        name = self.bs_saller.find('div', 'seller_info_area').find('h4').text
        phones = []
        for phone in self.bs_saller.find_all('div', 'phones_item'):
            span = phone.find('span')

            phones.append(self.strip_phone_number(span['data-phone-number']))
        saller = Seller(name=name, location=location, numbers_phones=phones)
        self.saller = self.find_saller(saller)


class AutoRia:
    page_count = 1
    soup = None
    page_sum = 0
    jump = range(5)

    def separator(self, l, *, n=2):
        result = [[]]
        current_index = 0
        for i, item in enumerate(l):
            if i != 0 and i % n == 0:
                result.append([])
                current_index += 1

            result[current_index].append(item)
        return result

    def pars_post(self, url: str):
        loc_soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        saller_obj = AutoRiaSaller(loc_soup.find('section', {'id': 'userInfoBlock'}))
        AutoRiaAuto(loc_soup, saller_obj.saller, url)

    def start(self):
        test = BeautifulSoup(requests.get('https://auto.ria.com/legkovie/').content, 'html.parser')
        x_test = test.find('div', {'id': 'pagination'}).find_all('span', {'class': 'page-item mhide'})[-1]
        self.page_sum = int(x_test.text.replace(' ', ''))
        for page in range(self.page_sum):
            self.base_page_pars()
            self.page_count += 1
            all_list = self.separator(self.soup.findAll('section', 'ticket-item'), n=4)
            for lst in all_list:
                try:
                    t1 = threading.Thread(target=self.pars_post, args=(lst[0]('a')[1]['href'],))
                    t2 = threading.Thread(target=self.pars_post, args=(lst[1]('a')[1]['href'],))
                    t3 = threading.Thread(target=self.pars_post, args=(lst[2]('a')[1]['href'],))
                    t4 = threading.Thread(target=self.pars_post, args=(lst[3]('a')[1]['href'],))
                    t1.start()
                    t2.start()
                    t3.start()
                    t4.start()
                    t1.join()
                    t2.join()
                    t3.join()
                    t4.join()
                except IndexError:
                    t1 = threading.Thread(target=self.pars_post, args=(lst[0]('a')[1]['href'],))
                    t2 = threading.Thread(target=self.pars_post, args=(lst[1]('a')[1]['href'],))
                    t1.start()
                    t2.start()
                    t1.join()
                    t2.join()

    def base_page_pars(self):
        self.soup = BeautifulSoup(
            requests.get('https://auto.ria.com/legkovie', params={'page': self.page_count}).content,
            'html.parser')
