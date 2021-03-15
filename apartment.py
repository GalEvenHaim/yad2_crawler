from dataclasses import dataclass
import datetime
import typing


@dataclass
class Apartment:
    link: str
    update: typing.Union[str, datetime.date]# todo(mor): use typing.Union
    street: str
    hood: str
    rooms: str
    floor: str
    square: str
    price: str
    more_info: str
    seller: str
    phone: str

    def __post_init__(self):
        if self.update == 'עודכן היום':
            self.update = str(datetime.date.today())
        else:
            try:
                self.update = str(datetime.datetime.strptime(self.update.split()[2].replace('/', '-'), '%d-%m-%Y').date())
            except:  # todo(mor): specific exception
                self.update = '01-01-2000'

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.street == other.street and self.hood == other.hood \
               and self.floor == other.floor and self.square == other.square  # todo(mor): why these 4?

    def __hash__(self):
        return hash(self.get_all()[1:]) # todo(mor): why this hash?

    def get_all(self):
        """
        returns a tuple containing the apartment's information
        :return: tuple
        """
        return self.link, self.update, self.street, self.hood, self.rooms, self.floor, self.square, self.price, \
               self.more_info, self.seller, self.phone
