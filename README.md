# Books-LLm
The intention for this repo is to showcase my web mining skills as well as my ability to implement ETL process
that would streamline the extraction process, transformation of the data as well as loading it into a database.
The data would later be used to feed an LLM in a RAG setup.

## Stack used so far
Extraction process:
- python requests
- python Beautiful Soup
- Playwright for alternative browser scraping

ETL process:
- Data lake: MinIO
- Database: PostgreSQL
- Orchestration: both Prefect and Airflow


## Project description
The end goal for this project is to simulate a book selling shop. The source used for the data is https://books.toscrape.com/ which is a website intended to be scraped and contains proxy data.
The idea is to collect all the data and then have the LLM do the selling of books as well as answer questions and give out suggestion about the books based on the information gathered.
