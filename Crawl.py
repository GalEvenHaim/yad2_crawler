from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from apartment import Apartment
import typing
import concurrent.futures


def get_driver():
    """
    returns a chrome webdriver with options set to headless, a non headless user agent and a window size of 1200X600
    :return:selenium.webdriver
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
    # Webdriver options:
    op = webdriver.ChromeOptions()
    #op.add_argument('--headless')
    op.add_argument(f'user-agent={user_agent}')
    op.add_argument('window-size=1200x600')
    return webdriver.Chrome(options=op)


def get_apartments_item_index(search_link: str):
    """
    Takes, the url of the search page and opens chrome to search result page,
    collects all the URL's to be crawled by threads.
    :param search_link: str
    :return: list
    """
    driver = get_driver()
    driver.get(search_link)
    res = []
    url = 'https://www.yad2.co.il/item/'
    try:
        numbers = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "numbers"))
                    )
        num_of_pages = min(3, int(numbers.find_element_by_tag_name("button").text))
    except TimeoutException:
        num_of_pages = 1
    for _ in range(num_of_pages):
        apartment_index = 0
        while True:  # scan all apartments in search page
            try:
                elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "feed_item_"+str(apartment_index)))
                )
                item = elem.get_attribute('item-id')
                if item:
                    res.append(url+item)
                apartment_index += 1
            except TimeoutException:
                break
        if num_of_pages == 1:
            break
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//*[contains(text(),'הבא')]"))
        )
        try:  # move to next search page
            button.click()
            title = driver.title
            # wait for page to change
            while title == driver.title:
                pass
        except ElementClickInterceptedException:
            break # no more result pages, exit for loop
    driver.quit()
    return res


def get_web_elem(func, elem: str, default=''):
    try:
        return func(elem)
    except NoSuchElementException:
        return default


def create_single_apartment(item: str) -> None:
    """
    opens a webdriver at 'https://www.yad2.co.il/item/' + item. crawls the web page
    creates an "Apartment" dataclass and adds it to the apartment_set
    :param item: str
    :return: None
    """
    driver = get_driver()
    driver.get(item)
    street = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "main_title"))
    ).text
    if hood := get_web_elem(driver.find_element_by_class_name, "description"):
        if hood := get_web_elem(hood.find_element_by_xpath, "//span/span[1]"):
            hood = hood.text
    if basic_info := get_web_elem(driver.find_element_by_class_name, "main_content"):
        if basic_info := get_web_elem(basic_info.find_element_by_class_name, "table"):
            lst = get_web_elem(basic_info.find_elements_by_class_name, "value", default=['', '', ''])  # [rooms, floor, sm]
    if price := get_web_elem(driver.find_element_by_tag_name, "strong"):
        price = price.text
    if more_info := get_web_elem(driver.find_element_by_tag_name, "section"):
        if more_info := get_web_elem(more_info.find_element_by_class_name, "wrapper_container"):
            more_info = more_info.text
    if seller := get_web_elem(driver.find_element_by_class_name, "seller"):
        seller = seller.text
    if butt := get_web_elem(driver.find_element_by_id, "lightbox_contact_seller_0"):
        butt.send_keys(Keys.ENTER)
        phone = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "phone_number"))
        )
    if update := get_web_elem(driver.find_element_by_class_name, 'top', default="01/01/2000"):
        if update := get_web_elem(update.find_element_by_class_name, 'left', default="01/01/2000"):
            update = update.text
    apartment_set.add(
        Apartment(item, update, street, hood, lst[0].text, lst[1].text, lst[2].text, price, more_info, seller,
                  phone.text))
    driver.close()


def start_crawling(url_list: typing.List):
    """
    creates threads according to number of WORKERS provided to program.
    sends threads to crawl the apartment web pages.
    :param url_list: list
    :return: None
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        for item in url_list:
            executor.submit(create_single_apartment, item)