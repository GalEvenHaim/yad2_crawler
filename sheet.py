import gspread
from oauth2client.service_account import ServiceAccountCredentials
import typing


def set_to_sheet(apartment_set: typing.Set):
    """
    takes a set of "Apartment" dataclasses and uploads it to google sheets.
    :param apartment_set: set
    :return: None
    """
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('yad_2_givataim').sheet1
    lst = sorted(apartment_set, key=lambda x: getattr(x, 'update'), reverse=True)
    sheet.clear()
    sheet.insert_row(['link', 'update', 'street', 'neighborhood', '# of rooms', 'floor', 's"m', 'price',
                      'about the property', 'seller', 'phone number'], 1)
    apartments_list = []
    for i in range(len(lst)):
        apartments_list.append(lst[i].get_all())
    sheet.insert_rows(apartments_list, 2)

