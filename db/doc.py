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
    model = StringField()
    price = DictField()
    image = StringField()
    data_created_auto = DateTimeField()

    saller = ReferenceField(Seller)

    location = StringField()

    driving_type = StringField()
    type_auto = StringField()
    fuel_type = StringField()
    engine_capacity = FloatField()
    duration = IntField()

    date_created_post = DateTimeField()
    date_updated = DateTimeField()

    autoria_link = StringField()
    rst_link = StringField()
    olx_link = StringField()

    def __str__(self):
        return f'<PostAuto: mark={self.mark}, model={self.model}, year={self.data_created_auto}, image={self.image}, price={self.price}, autoria_link={self.autoria_link}, location={self.location}, driving_type={self.driving_type}, type_auto={self.type_auto}, engine_capacity={self.engine_capacity}, fuel_type={self.fuel_type}, duration={self.duration}>'

