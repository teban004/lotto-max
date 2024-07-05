from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import logging
import psycopg2
from psycopg2 import Error
import configparser

logging.basicConfig(filename='logs/lotto-max.log',
                    filemode='a',
                    format='%(asctime)s; %(levelname)s; %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def scrape_page(url):
    try:
        with sync_playwright() as p:
            # Step 1: Launch the browser with Chromium
            browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium')
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
                logger.error(f'Section with class="current-result-date" not found')
                return None

            # Step 8: Extract the desired data
            date_text = date_section.get_text().strip()
            logger.info(f'Found results for the date {date_text}')

            date_object = datetime.strptime(date_text, "%A, %B %d, %Y")

            numbers_section = soup.find('div', {'class': 'play-content'})
            winning_numbers_html = numbers_section.find_all('div', {'class': 'ball-number'})
            if not winning_numbers_html:
                raise ValueError("Couldn't find the winning numbers on the page.")
            winning_numbers = list()
            for winning_num in winning_numbers_html:
                winning_numbers.append(winning_num.get_text().strip())
            logger.info(f"Winning numbers: {winning_numbers}")

            return date_object.strftime('%Y-%m-%d'), winning_numbers

    except Exception as e:
        logger.error(f'An error occurred: {e}')
        return None


def read_db_config(filename='programacion/lotto-max/config.ini', section='postgresql'):
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
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        return None

def check_if_row_exists(conn, check_date):
    """ Check if a row with the given date exists in the table """
    try:
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM lotto_max_results WHERE draw_date = %s"
        cursor.execute(query, (check_date,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    except (Exception, Error) as error:
        logger.error(f"Error checking if row exists: {error}")
        return False

def insert_row_if_not_exists(conn, insert_date, other_values):
    """ Insert a row if it doesn't already exist """
    try:
        cursor = conn.cursor()
        insert_query = "INSERT INTO lotto_max_results (draw_date, number1, number2, number3, number4, number5, number6, number7, bonus_number) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (insert_date, other_values[0], other_values[1], other_values[2], other_values[3], other_values[4], other_values[5], other_values[6], other_values[7]))
        conn.commit()
        if cursor.rowcount > 0:
            logger.info("Numbers inserted into the db successfully.")
        else:
            logger.info("No rows were inserted into the db.")
        cursor.close()
    except (Exception, Error) as error:
        conn.rollback()
        logger.error(f"Error inserting row: {error}")

def main():
    # URL of the OLG Lotto Max past results page
    url = "https://www.olg.ca/en/lottery/play-lotto-max-encore/past-results.html"

    draw_date, winning_numbers = scrape_page(url)
    if not draw_date:
        logger.error('Failed to scrape the page')

    try:
        # Read database configuration from config file
        db_config = read_db_config()

        # Connect to the database
        conn = connect_to_database(db_config)
        if conn is None:
            return
        try:
            # Check if row exists
            if not check_if_row_exists(conn, draw_date):
                # Insert row if it doesn't exist
                insert_row_if_not_exists(conn, draw_date, winning_numbers)
        finally:
            # Close database connection
            conn.close()
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()