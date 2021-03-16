# yad2 Crawler

##Goal
Search for apartments on yad2.co.il according to specific properties,
upload the results to a google sheet spreadsheet.

###Flow:
1. Enter your search parameters.
2. The program will open Chrome and search for apartments on yad2.co.il
3. The program will start crawling the search results in a multithreaded way.
4. Crawled information will be uploaded to google sheets.

###Requirements
 - Selenium. https://selenium-python.readthedocs.io/installation.html
 - gspread: an API gor google sheets https://gspread.readthedocs.io/en/latest/
 - oauth2client: handles connection to google API OAuth2-protected resources https://oauth2client.readthedocs.io/en/latest/

###Program arguments
 - city: which city to search.
 - min_rooms: min number of rooms.
 - max_rooms max number of rooms.
 - max_price: price limit
 - min_sqr: min of square meter
 - workers: determine number of threads to be created