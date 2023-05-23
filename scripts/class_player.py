from uuid import uuid4

sex_dict = {'M': 'M', 'F': 'F', 'W': 'F', 'D': 'D'}
titles = ("CM", "FM", "IM", "GM", "WCM", "WFM", "WIM", "WGM")


class Player:
    def __init__(
            self, name, sex=None, birthday=None, country=None, title=None, rating=0, uuid=None,
            uuid_associate="00000000-0000-0000-0000-000000000000"
    ):
        self.name = self.sex = self.birthday = self.country = self.title = self.rating = None
        self.set_name(name)
        self.set_sex(sex)
        self.set_birthday(birthday)
        self.set_country(country)
        self.set_title(title)
        self.set_rating(rating)
        self.uuid = uuid or str(uuid4())
        self.uuid_associate = uuid_associate

    def __str__(self):
        return self.name

    def copy(self):
        return Player(
            self.get_name(), self.get_sex(), self.get_birthday(), self.get_country(), self.get_title(),
            self.get_rating(), self.get_uuid(), self.get_uuid_associate()
        )

    def get_uuid(self):
        return self.uuid

    def get_uuid_associate(self):
        return self.uuid_associate

    def set_uuid_associate(self, uuid_associate):
        self.uuid_associate = uuid_associate

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_sex(self):
        return self.sex

    def set_sex(self, sex):
        if sex in sex_dict:
            self.sex = sex_dict[sex]

    def get_birthday(self):
        return self.birthday

    def set_birthday(self, birthday):
        if isinstance(birthday, int) or (isinstance(birthday, str) and birthday.isdigit()):
            self.birthday = int(birthday)

    def get_country(self):
        return self.country

    def set_country(self, country):
        self.country = country

    def get_title(self):
        return self.title

    def set_title(self, title):
        if title in titles:
            self.title = title

    def get_rating(self):
        return self.rating

    def set_rating(self, rating):
        if isinstance(rating, int) or (isinstance(rating, str) and rating.isdigit()):
            self.rating = int(rating)

    def get_data(self):
        return self.get_name(), self.get_sex(), self.get_birthday(), self.get_country(), self.get_title(), \
               self.get_rating(), self.get_uuid(), self.get_uuid_associate()

    def is_valid(self):
        return self.get_name() != ""
