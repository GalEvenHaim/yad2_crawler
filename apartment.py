from dataclasses import dataclass, field
import datetime
from typing import Any


@dataclass
class Apartment:
    link: str
    update: Any
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
            except:
                self.update = '01-01-2000'


    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.street == other.street and self.hood == other.hood\
               and self.floor == other.floor and self.square == other.square

    def __hash__(self):
        return hash(self.get_all()[1:])

    def get_all(self):
        """
        returns a tuple containing the apartment's information
        :return: tuple
        """
        return self.link, self.update, self.street, self.hood, self.rooms, self.floor, self.square, self.price, self.more_info, self.seller, self.phone
