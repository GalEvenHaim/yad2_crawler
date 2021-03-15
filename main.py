from Crawl import get_apartments_item_index
from Crawl import start_crawling
from sheet import set_to_sheet
import argparse


def args_parse():
    parser = argparse.ArgumentParser(
        description="A program to search for appartments in yad_2 according to given city, number of rooms and price "
                    "range")
    parser.add_argument("c", "--city", default="Givataym", type=str, choices=["Givataym", "Tel Aviv", "Ramat Gan"],
                        help="choose between Givataym, Tel Aviv, and Ramat Gan")
    parser.add_argument("min_rooms", type=str, help="min number of rooms")
    parser.add_argument("max_rooms",  type=str, help="max number of rooms")
    parser.add_argument("max_price",  type=str, help="price limit")
    parser.add_argument("min_sqr",  type=str, help="min of square meter")
    parser.add_argument("workers", type=int, help="determine number of threads to be created")
    args = parser.parse_args()
    return args


def main():
    args = args_parse()
    city_dict = {"Givataym": "6300", "Tel Aviv": "5000", "Ramat Gan": "8600"}
    WORKERS = args.workers
    search_link = f"https://www.yad2.co.il/realestate/forsale?city={city_dict[args.city]}" \
                  f"&rooms={args.min_rooms}-{args.max_rooms}&price=-1-{args.max_price}&parking=1&elevator=1&squaremeter={args.min_sqr}--1"
    print(f"finding apartments in {args.city} with  {args.min_rooms}-{args.max_rooms} rooms ")
    apartment_set = set()
    item_list = get_apartments_item_index()
    print(f"found {len(item_list)} apartments.")
    start_crawling(item_list)
    set_to_sheet(apartment_set)
    print(f"uploaded {len(apartment_set)} to google sheets.")


main()