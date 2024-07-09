from __future__ import annotations
from .type_declerations import Player_Data
from ..common.object import Object

SEX_DICT = {'M': 'M', 'F': 'F', 'W': 'F', 'D': 'D'}
TITLES = ("GM", "IM", "WGM", "FM", "WIM", "CM", "WFM", "WCM")


class Player(Object):
    def __init__(
            self, name: str, sex: str | None = None, birthday: int | str | None = None, country: str | None = None,
            title: str | None = None, rating: int | str | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000000"
    ) -> None:
        super().__init__(name, uuid, uuid_associate)
        self.sex: str | None = None
        self.birthday: int | None = None
        self.country: str | None = None
        self.title: str | None = None
        self.rating: int | None = None
        self.set_sex(sex)
        self.set_birthday(birthday)
        self.set_country(country)
        self.set_title(title)
        self.set_rating(rating)

    def copy(self) -> Player:
        return Player(
            self.get_name(), self.get_sex(), self.get_birthday(), self.get_country(), self.get_title(),
            self.get_rating(), self.get_uuid(), self.get_uuid_associate()
        )

    def get_sex(self) -> str | None:
        return self.sex

    def get_birthday(self) -> int | None:
        return self.birthday

    def get_country(self) -> str | None:
        return self.country

    def get_title(self) -> str | None:
        return self.title

    def get_rating(self) -> int | None:
        return self.rating

    def get_data(self) -> Player_Data:
        return self.get_name(), self.get_sex(), self.get_birthday(), self.get_country(), self.get_title(), \
               self.get_rating(), self.get_uuid(), self.get_uuid_associate()

    def set_sex(self, sex: str | None) -> None:
        if sex == "" or sex is None:
            self.sex = None
        elif sex.upper() in SEX_DICT:
            self.sex = SEX_DICT[sex.upper()]

    def set_birthday(self, birthday: int | str | None) -> None:
        if isinstance(birthday, int) or (isinstance(birthday, str) and birthday.isdigit()):
            self.birthday = int(birthday)
        elif birthday == "" or birthday is None:
            self.birthday = None

    def set_country(self, country: str | None) -> None:
        if bool(country):
            self.country = country
        else:
            self.country = None

    def set_title(self, title: str | None) -> None:
        if title in TITLES:
            self.title = title
        elif title == "" or title is None:
            self.title = None

    def set_rating(self, rating: int | str | None) -> None:
        if isinstance(rating, int) or (isinstance(rating, str) and rating.isdigit()):
            self.rating = int(rating)
        elif rating == "" or rating is None:
            self.rating = None

    def is_valid(self) -> bool:
        return bool(self.get_name())
