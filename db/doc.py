from mongoengine import *

connect('pars_auto')


class Seller(Document):
    name = StringField()
    numbers_phones = ListField(StringField())
    site_register = StringField()
    location = StringField()

    def __str__(self):
        return f'<Saller: name={self.name}, numbers_phones={self.numbers_phones}, location={self.location}>'


class PostAuto(Document):

    mark = StringField()
    model = DictField()
    price = IntField()
    image = StringField()
    data_created_auto = DateTimeField()

    saller = ReferenceField(Seller)

    location = StringField()

    driving_type = StringField()
    type_auto = StringField()
    fuel_type = StringField()
    engine_capacity = StringField()
    duration = IntField()

    date_created_post = DateTimeField()
    date_updated = DateTimeField()

    autoria_link = StringField()
    rst_link = StringField()
    olx_link = StringField()


