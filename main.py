from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from apartment import *
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from sheet import *
import sys
import argparse
from time import time, sleep
import threading
import concurrent.futures

start_time = time()

parser = argparse.ArgumentParser(description="a program to search for appartments in yad_2 according to given city, number of rooms and price range")
parser.add_argument("-c","--city", default="Givataym", type=str, choices=["Givataym", "Tel Aviv", "Ramat Gan"], help="choose between Givataym, Tel Aviv, and Ramat Gan")
parser.add_argument("--min_rooms", default="4", type=str)
parser.add_argument("-r", "--max_rooms", default="5", type=str)
parser.add_argument("-p", "--max_price", default="2750000", type=str)
parser.add_argument("-s", "--min_sqr", default="90", type=str)
parser.add_argument("-w", "--workers", default=5, type=int, help="determine number of threads to be created")

apartment_set = set()
city_dict = {"Givataym":"6300", "Tel Aviv": "5000" , "Ramat Gan": "8600"}
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
ITEM = 'https://www.yad2.co.il/item/'
args = parser.parse_args()
WORKERS = args.workers
SEARCH_LINK = f"https://www.yad2.co.il/realestate/forsale?city={city_dict[args.city]}" \
              f"&rooms={args.min_rooms}-{args.max_rooms}&price=-1-{args.max_price}&parking=1&elevator=1&squaremeter={args.min_sqr}--1"

# Webdriver options:
op = webdriver.ChromeOptions()
op.add_argument('--headless')
op.add_argument(f'user-agent={user_agent}')
op.add_argument('window-size=1200x600')


def get_apartments_item_index():
    """
    Opens chrome to search result page, collects all the URL's to be crawled by threads.
    :return: list
    """
    driver = webdriver.Chrome(options=op)
    driver.get(SEARCH_LINK)
    res = []
    try:
        numbers = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "numbers"))
                    )
        num_of_pages = min(3, int(numbers.find_element_by_tag_name("button").text))
    except TimeoutException:
        num_of_pages = 1
    for _ in range(num_of_pages):
        i=0
        while True:  # scan all apartments in search page
            try:
                elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "feed_item_"+str(i)))
                )
                item = elem.get_attribute('item-id')
                if item is not None:
                    res.append(ITEM+item)
                i += 1
            except TimeoutException:
                break
        if num_of_pages == 1:
            break
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//*[contains(text(),'הבא')]"))
        )
        try:  # move to next search page
            button.click()
            time.sleep(5)
        except ElementClickInterceptedException:
            break
    driver.quit()
    return res


def create_single_apartment(item:str):
    """
    opens a webdriver at 'https://www.yad2.co.il/item/' + item. crawls the web page
    creates an apartment and adds it to the apartment_set
    :param item: str
    :return: None
    """
    driver = webdriver.Chrome(options=op)
    driver.get(item)
    street = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "main_title"))
    ).text
    hood = driver.find_element_by_class_name("description").find_element_by_xpath("//span/span[1]").text
    basic_info = driver.find_element_by_class_name("main_content").find_element_by_class_name("table")
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


def start_crawling(url_list: list):
    """
    creates threads according to number of WORKERS provided to program.
    sends threads to crawl the apartment web pages.
    :param url_list: list
    :return: None
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        for item in url_list:
            try:
                executor.submit(create_single_apartment, item)
            except TimeoutException:
                apartment_set.add(Apartment(item, '', '', '', '', '', '', '', '', '', ''))


if __name__ == '__main__':
    print(f"finding apartments in {args.city} with  {args.min_rooms}-{args.max_rooms} rooms ")
    item_list = get_apartments_item_index()
    print(f"found {len(item_list)} apartments.")
    start_crawling(item_list)
    set_to_sheet(apartment_set)
    print(f"uploaded {len(apartment_set)} to google sheets.")


    end_time = time()
    elapsed_time = end_time - start_time
    print(f"time is: {elapsed_time}")
