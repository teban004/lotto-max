from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import logging
import psycopg2
from psycopg2 import Error
import configparser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_page(url):
    try:
        with sync_playwright() as p:
            # Step 1: Launch the browser with Chromium
            browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium-browser')
            page = browser.new_page()

            # Step 2: Fetch the web page content
            logger.info(f'Navigating to {url}')
            page.goto(url)

            # Step 3: Give the page time to load all JavaScript content
            page.wait_for_load_state('networkidle')

            # Step 4: Get the rendered page content
            web_content = page.content()
            with open('contenido_pagina.html', 'w') as f:
                f.write(web_content)

            # Step 5: Close the browser
            browser.close()

            # Step 6: Parse the web page content
            soup = BeautifulSoup(web_content, 'html.parser')

            # Step 7: Find the section you want to scrape
            date_section = soup.find('p', {'class': 'current-result-date'})
            if date_section is None:
                logger.error(f'Section with id "main-content" not found')
                return None

            # Step 8: Extract the desired data
            date_text = date_section.get_text().strip()
            logger.info(f'Found results for the date {date_text}')

            date_object = datetime.strptime(date_text, "%A, %B %d, %Y")

            numbers_section = soup.find('div', {'class': 'play-content'})
            winning_numbers_html = numbers_section.find_all('div', {'class': 'ball-number'})
            if not winning_numbers_html:
                raise ValueError("Couldn't find the winning numbers on the page.")
            logger.info(f"Winning numbers:")
            winning_numbers = list()
            for winning_num in winning_numbers_html:
                logger.info(f"{winning_num.get_text().strip()}")
                winning_numbers.append(winning_num.get_text().strip())
            return date_object.strftime('%Y-%m-%d'), winning_numbers

    except Exception as e:
        logger.error(f'An error occurred: {e}')
        return None


def read_db_config(filename='config.ini', section='postgresql'):
    """ Read database configuration from a file """
    parser = configparser.ConfigParser()
    parser.read(filename)

    # Get section, default to postgresql
    db_config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return db_config


def connect_to_database(db_config):
    """ Connect to the PostgreSQL database """
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except (Exception, Error) as error:
        print(f"Error while connecting to PostgreSQL: {error}")
        return None


if __name__ == '__main__':
    # URL of the OLG Lotto Max past results page
    url = "https://www.olg.ca/en/lottery/play-lotto-max-encore/past-results.html"

    content = scrape_page(url)
    if content:
        print(content)
        conn = connect_to_database()
    else:
        logger.error('Failed to scrape the page')
