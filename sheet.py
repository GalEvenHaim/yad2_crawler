import gspread
from oauth2client.service_account import ServiceAccountCredentials
from main import *

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

client = gspread.authorize(creds)

sheet = client.open('yad_2_givataim').sheet1

def set_to_sheet(apartment_set):
    lst = sorted(apartment_set, key=lambda x: getattr(x, 'update'), reverse=True)
    sheet.clear()
    sheet.insert_row(['קישור', 'תאריך עדכון', 'רחוב', 'שכונה', 'חדרים', 'קומה ', 'מ"ר', 'מחיר', 'על הנכס', 'שם המוכר', 'טלפון'],1)
    #sheet.delete_rows(2, sheet.row_count)
    #app_values = [app.get_all() for app in lst]
    l1 = []
    for i in range(len(lst)):
        l1.append(lst[i].get_all())
    sheet.insert_rows(l1, 2)

