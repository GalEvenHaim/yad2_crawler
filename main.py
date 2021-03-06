from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from apartment import *
from selenium.common.exceptions import NoSuchElementException
from sheet import *
import sys
import argparse

city_dict = {"Givataym":"6300", "Tel Aviv": "5000" , "Ramat Gan": "8600"}
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
ITEM = 'https://www.yad2.co.il/item/'
op = webdriver.ChromeOptions()
op.add_argument('--headless')
op.add_argument(f'user-agent={user_agent}')
op.add_argument('window-size=1200x600')
apartment_set = set()
parser = argparse.ArgumentParser(description="a program to search for appartments in yad_2 according to given city, number of rooms and price range")
parser.add_argument("-c","--city", default="Givataym", type=str, choices=["Givataym", "Tel Aviv", "Ramat Gan"], help="choose between Givataym, Tel Aviv, and Ramat Gan")
parser.add_argument("--min_rooms", default="4", type=str)
parser.add_argument("-r", "--max_rooms", default="5", type=str)
parser.add_argument("-p", "--max_price", default="2750000", type=str)
parser.add_argument("-s", "--min_sqr", default="90", type=str)

args = parser.parse_args()
SEARCH_LINK = f"https://www.yad2.co.il/realestate/forsale?city={city_dict[args.city]}" \
              f"&rooms={args.min_rooms}-{args.max_rooms}&price=-1-{args.max_price}&parking=1&elevator=1&squaremeter={args.min_sqr}--1"

def get_apartments_item_index(driver: webdriver):

    res = []
    try:
        numbers = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "numbers"))
                    )
        num_of_pages = min(3, int(numbers.find_element_by_tag_name("button").text))
    except:
        num_of_pages = 1
    for _ in range(num_of_pages):
        i=0
        while True:
            try:
                elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "feed_item_"+str(i)))
                )
                item = elem.get_attribute('item-id')
                if item is not None:
                    res.append(ITEM+item)
                i += 1
            except:
                break
        # driver.find_element_by_xpath(".//*[contains(text(),'הבא')]").click()
        if num_of_pages == 1:
            break
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//*[contains(text(),'הבא')]"))
        )
        try:
            button.click()
            time.sleep(5)  # to do: replace this with a more elegant solution
        except:
            break
    return res

def create_single_apartment(item, ow):
    driver.execute_script(f"window.open('{item}','_blank');")
    curr = driver.window_handles[-1]
    driver.switch_to.window(curr)
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "content"))
    )
    street = WebDriverWait(elem, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "main_title"))
    ).text

    hood = driver.find_element_by_class_name("content").find_element_by_class_name("description").text
    basic_info = driver.find_element_by_class_name("content").find_element_by_class_name("table")
    lst = basic_info.find_elements_by_class_name("value")  # [rooms, floor, sm]
    price = driver.find_element_by_tag_name("strong").text
    more_info = driver.find_element_by_tag_name("section").find_element_by_class_name("wrapper_container").text
    seller = driver.find_element_by_class_name("seller").text
    butt = driver.find_element_by_id("lightbox_contact_seller_0")
    butt.send_keys(Keys.ENTER)
    phone = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "phone_number"))
    )
    try:
        update = driver.find_element_by_class_name('top').find_element_by_class_name('left').text
    except NoSuchElementException:
        update = "01/01/2000"
    apartment_set.add(
        Apartment(item, update, street, hood, lst[0].text, lst[1].text, lst[2].text, price, more_info, seller,
                  phone.text))
    driver.close()
    driver.switch_to.window(ow)


def create_apartments(driver: webdriver, items):
    ow = driver.current_window_handle
    for item in items:
        try:
            create_single_apartment(item, ow)
        except :
            print("exception in for loop", sys.exc_info())
            apartment_set.add(Apartment(item))


if __name__ == '__main__':
    driver = webdriver.Chrome(options= op)
    driver.get(SEARCH_LINK)
    item_list = get_apartments_item_index(driver)
    #s1 = set(item_list)
    create_apartments(driver, item_list)
    set_to_sheet(apartment_set)
    driver.quit()
