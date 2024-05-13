import requests
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin


class HTML_Scraper:
    links: List[str]
    data: List[dict]
    domain = "https://books.toscrape.com/"
    home_page: str = "https://books.toscrape.com/index.html"

    def collect_links(self):
        req = requests.get(self.home_page)
        page = BeautifulSoup(req.text, 'lxml')

        self.links.extend(self.scrape_single_page(page))

    @staticmethod
    def scrape_single_page(soup: BeautifulSoup) -> List[str]:
        list_of_books = soup.find("ol", class_='row')
        if list_of_books:
            books_links = list_of_books.find_all('li')
            if books_links:
                return [link.h3.a['href'] for link in books_links]

    def extract_data(self, link: str) -> dict:
        req = requests.get(link)
        page = BeautifulSoup(req.text, 'lxml')

        book = {}
        book['category'] = self.scrape_category(page)
        book['title'] = self.scrape_title(page)
        book['price'] = self.scrape_price(page)
        book['rating'] = self.scrape_rating(page)


        return book

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
        check = page.find("div", {"id": "product_description"})
        if check:
            return check.next_sibling.next_sibling.text.strip()


