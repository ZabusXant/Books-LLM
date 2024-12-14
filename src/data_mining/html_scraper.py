import requests
from requests import Response
from bs4 import BeautifulSoup, Tag
from typing import List
from urllib.parse import urljoin
import pandas as pd
from utils.minio_interaction import MinIO
from utils.postgres_interaction import Database


# noinspection PyArgumentList
class HTML_Scraper(MinIO, Database):
    links: List[str] = []
    data: List[dict] = []
    domain = "https://books.toscrape.com/"
    home_page: str = "https://books.toscrape.com/index.html"

    def __init__(self):
        MinIO.__init__(self)
        Database.__init__(self)

    def collect_links(self):
        req = requests.get(self.home_page)
        page = BeautifulSoup(req.text, 'lxml')
        self.links.extend(self.scrape_single_page(req))
        next_page = page.find("ul", class_='pager').find("li", class_='next')

        page_counter = 1
        while next_page:
            next_page = page.find("ul", class_='pager').find("li", class_='next')
            if next_page:
                req = requests.get(urljoin(req.url, next_page.a['href']))
                page = BeautifulSoup(req.text, 'lxml')
                self.links.extend(self.scrape_single_page(req))
                page_counter += 1
                if page_counter % 10 == 0:
                    print("Went through", page_counter, "pages")

    @staticmethod
    def scrape_single_page(req: Response) -> List[str]:
        soup = BeautifulSoup(req.text, 'lxml')
        list_of_books = soup.find("ol", class_='row')
        if list_of_books:
            books_links = list_of_books.find_all('li')
            if books_links:
                return [urljoin(req.url, link.h3.a['href']) for link in books_links]

    def collect_data(self):

        for link in self.links:
            self.data.append(self.extract_data(link))
            if len(self.data) % 100 == 0:
                print("Extracted", len(self.data), "links.")

        print("Finished with", len(self.data), "records extracted.")

    def extract_data(self, link: str) -> dict:
        req = requests.get(link)
        req.encoding = req.apparent_encoding
        page = BeautifulSoup(req.text, 'lxml')

        book = {'category': self.scrape_category(page),
                'title': self.scrape_title(page),
                'price': self.scrape_price(page),
                'rating': self.scrape_rating(page),
                'description': self.scrape_book_description(page),
                'availability': self.scrape_availability(page)}

        return book

    @staticmethod
    def check_next_page(page: BeautifulSoup) -> Tag:
        check = page.find("ul", class_='pager')
        if check:
            return check.find("li", class_='next')

    @staticmethod
    def scrape_category(soup: BeautifulSoup) -> str:
        check = soup.find("ul", class_="breadcrumb")
        if check:
            return check.find_all('li')[-2].text.strip()

    @staticmethod
    def scrape_title(soup: BeautifulSoup) -> str:
        check = soup.find('div', class_='product_main')
        if check:
            return check.h1.text.strip()

    @staticmethod
    def scrape_price(soup: BeautifulSoup) -> str:
        check = soup.find('div', class_='product_main')
        if check:
            return check.p.text.strip()

    @staticmethod
    def scrape_rating(soup: BeautifulSoup) -> str:
        check = soup.find("p", class_='star-rating')
        if check:
            return check['class'][-1]

    @staticmethod
    def scrape_book_description(soup: BeautifulSoup) -> str:
        check = soup.find("div", {"id": "product_description"})
        if check:
            return check.next_sibling.next_sibling.text.strip()

    @staticmethod
    def scrape_availability(soup: BeautifulSoup) -> str:
        check = soup.find("p", class_='instock availability')
        if check:
            return check.text.strip()

    def store_data(self):
        data = pd.DataFrame(self.data)
        self.upload_df_to_minio(bucket='raw-data', file_name='html_raw_data.csv', df=data)
        self.upload_df_to_table(table_name='html_raw_data', data=data)

    def run_crawler(self):
        self.collect_links()
        print("Collected", len(self.links), "links")
        self.collect_data()
        self.store_data()
