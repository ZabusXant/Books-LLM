from playwright._impl._errors import Error
from playwright.sync_api import Browser, Page, Response, sync_playwright
from playwright.sync_api._context_manager import PlaywrightContextManager
from urllib.parse import urljoin
from typing import List, Optional
import pandas as pd
import re


class Browser_Scraper:
    browser: Browser
    page: Page
    playwright: PlaywrightContextManager
    headless: bool = True
    links: List[str] = []
    data: List[dict] = []
    home_page: str = "https://books.toscrape.com/index.html"

    def __init__(self, headless: bool = True) -> None:
        import nest_asyncio

        nest_asyncio.apply()
        self.playwright = sync_playwright().start()
        self.headless = headless
        self.start_browser()

    def start_browser(self):
        self.browser: Browser = self.playwright.firefox.launch(headless=self.headless)
        self.page = self.browser.new_page()

    def open_page(self, url: str) -> Response:
        try:
            response: Response = self.page.goto(url, wait_until="networkidle")
        except Error as e:
            print(e)
            return None
        return response

    # =====================================
    #Functions above this line are used to set up the functions to work with the browser
    #Functions from here on out will be used for the actual scraping of the data

    def collect_links(self):
        self.open_page(self.home_page)

        while True:
            self.links.extend(self.scrape_single_page())

            next_button = self.page.get_by_role("link", name="next", exact=True)
            if next_button.count() > 0:
                next_button.click()
            else:
                break

    def scrape_single_page(self) -> List[str]:
        list_of_books = self.page.query_selector_all("article.product_pod")
        if len(list_of_books) > 0:
            return [urljoin(self.page.url, book.query_selector("a").get_attribute('href')) for book in list_of_books]

    def extract_data(self, link: str) -> dict:
        self.open_page(link)

        book = {'category': self.scrape_category(),
                'title': self.scrape_title(),
                'price': self.scrape_price(),
                'rating': self.scrape_rating(),
                'description': self.scrape_description(),
                'availability': self.scrape_availability()}

        return book

    def scrape_category(self):
        check = self.page.query_selector("ul.breadcrumb").query_selector_all("li")
        if len(check) > 2:
            return check[-2].inner_text().strip()

    def scrape_title(self):
        check = self.page.query_selector("h1")
        if check:
            return check.inner_text().strip()

    def scrape_price(self):
        check = self.page.query_selector("p.price_color")
        if check:
            return check.inner_text().strip()

    def scrape_rating(self):
        check = self.page.query_selector("p.star-rating")
        if check:
            return check.get_attribute("class").split(" ")[-1]

    def scrape_description(self):
        check = self.page.query_selector("article > p")
        if check:
            return check.inner_text().strip()

    def scrape_availability(self):
        check = self.page.query_selector("p.instock")
        if check:
            return check.inner_text().strip()

    def collect_data(self):
        self.collect_links()

        for link in self.links:
            self.data.append(self.extract_data(link))

    def process_data(self):
        df = pd.DataFrame(self.data)
        df.to_csv("../data/browser_data.csv", index=False, sep='^', encoding='utf-8')

        df['category'] = df['category'].apply(self.process_category)
        df['price'] = df['price'].apply(self.process_price)
        df['rating'] = df['rating'].apply(self.process_rating)
        df['description'] = df['description'].apply(self.process_description)
        df['availability'] = df['availability'].apply(self.process_availability)

        df.to_csv("../data/browser_data_processed.csv", index=False, sep='^', encoding='utf-8')

    @staticmethod
    def process_category(st: str) -> str:
        return "Uncategorized" if st == "Default" else st

    @staticmethod
    def process_price(st: str) -> float:
        return float(st.replace("£", ''))

    @staticmethod
    def process_rating(st: str) -> int:
        ratings = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

        return ratings[st]

    @staticmethod
    def process_description(st: str) -> Optional[str]:
        if isinstance(st, str):
            return st[:-8]
        else:
            return None

    @staticmethod
    def process_availability(st: str) -> int:
        return int(re.sub(r"\D", '', st))

    def run_crawler(self):
        self.collect_links()
        self.collect_data()
        self.process_data()


if __name__ == "__main__":
    scraper = Browser_Scraper(False)
    scraper.run_crawler()
    print('debug')
