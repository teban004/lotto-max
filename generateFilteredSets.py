import psycopg2
from itertools import combinations
from collections import defaultdict
from psycopg2 import Error
import logging
import configparser
import psycopg2.extras
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import os
from dotenv import load_dotenv
from typing import List, Tuple, Optional

load_dotenv()

logging.basicConfig(filename='logs/generateFilteredSets.log',
                    filemode='a',
                    format='%(asctime)s; %(levelname)s; %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_historical_sets() -> List[Tuple[str, set]]:
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("SELECT draw_date, number1, number2, number3, number4, number5, number6, number7, bonus_number FROM public.lotto_max_results")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Convert each row to a tuple: (draw_date, set of numbers)
    return [(r[0], set(r[1:])) for r in rows]

def match_rule_1(candidate: Tuple[int, ...], winning_set: set) -> bool:
    # Return True if candidate matches 5 or more numbers in winning_set
    return len(set(candidate) & winning_set) >= 5

def match_rule_2(candidate: Tuple[int, ...], winning_set: set) -> bool:
    # Return True if candidate has 4 or more numbers that are +/- 1 of any number in winning_set
    count = 0
    for num in candidate:
        if num in winning_set:
            count += 1
            winning_set.remove(num)  # Avoid double counting
        elif (num - 1 in winning_set) or (num + 1 in winning_set):
            count += 1
            winning_set.remove(num - 1 if (num - 1 in winning_set) else num + 1)
        if count >= 4:
            return True
    return False

def match_rule_3(candidate: Tuple[int, ...]) -> bool:
    # Return False if candidate has 4 or more consecutive numbers
    sorted_candidate = sorted(candidate)
    consecutive_count = 0
    for i in range(1, len(sorted_candidate)):
        if sorted_candidate[i] == sorted_candidate[i - 1] + 1:
            consecutive_count += 1
            if consecutive_count >= 4:
                return True
    return False

def insert_batch(batch: List[Tuple[int, ...]]) -> None:
    conn = connect_to_database()
    try:
        with conn:
            with conn.cursor() as cur:
                insert_query = """
                INSERT INTO public.filtered_lotto_sets
                (number1, number2, number3, number4, number5, number6, number7)
                VALUES %s
                ON CONFLICT DO NOTHING;
                """
                psycopg2.extras.execute_values(cur, insert_query, batch)
        logger.info(f"Inserted batch of {len(batch)} sets.")
    except Exception as e:
        logger.error(f"Error during batch insertion: {e}")
    finally:
        conn.close()

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

def connect_to_database():
    """Connect to the PostgreSQL database using environment variables."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except (Exception, Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        return None

def process_combinations(start, end, historical_sets):
    """Process a range of combinations and return rejected and accepted sets."""
    batch_rejected = []
    number_of_accepted_sets = 0
    number_of_rejected_sets_rule_1 = 0
    number_of_rejected_sets_rule_2 = 0
    number_of_rejected_sets_rule_3 = 0

    logger.info('Starting combination generation and filtering for range %d to %d.', start, end)
    for candidate in combinations(range(1, 51), 7):
        if start <= hash(candidate) % 99884400 < end:  # Divide work based on hash
            for draw_date, winning_set in historical_sets:
                if match_rule_1(candidate, winning_set):
                    batch_rejected.append(candidate)
                    number_of_rejected_sets_rule_1 += 1
                    break
                elif match_rule_2(candidate, winning_set):
                    batch_rejected.append(candidate)
                    number_of_rejected_sets_rule_2 += 1
                    break
            else:
                if match_rule_3(candidate):
                    batch_rejected.append(candidate)
                    number_of_rejected_sets_rule_3 += 1
                else:
                    number_of_accepted_sets += 1

    logger.info('Finished processing range %d to %d. Accepted: %d, Rejected: %d (Rule 1: %d, Rule 2: %d, Rule 3: %d)',
                start, end, number_of_accepted_sets,
                number_of_rejected_sets_rule_1 + number_of_rejected_sets_rule_2 + number_of_rejected_sets_rule_3,
                number_of_rejected_sets_rule_1,
                number_of_rejected_sets_rule_2,
                number_of_rejected_sets_rule_3)
    return batch_rejected, number_of_accepted_sets, number_of_rejected_sets_rule_1, number_of_rejected_sets_rule_2, number_of_rejected_sets_rule_3

def main():
    logger.info('Starting filtered set generation process.')
    try:
        historical_sets = load_historical_sets()
        logger.info(f'Loaded {len(historical_sets)} historical sets.')

        BATCH_SIZE = 1000
        total_accepted = 0
        total_rejected_rule_1 = 0
        total_rejected_rule_2 = 0
        total_rejected_rule_3 = 0

        # Parallel processing
        with ProcessPoolExecutor() as executor:
            futures = []
            num_workers = 2  # Adjust based on your CPU cores
            step = 99884400 // num_workers
            for i in range(num_workers):
                start = i * step
                end = (i + 1) * step
                futures.append(executor.submit(process_combinations, start, end, historical_sets))

            for future in tqdm(futures, total=num_workers):
                batch_rejected, accepted, rejected_1, rejected_2, rejected_3 = future.result()
                insert_batch(batch_rejected)
                total_accepted += accepted
                total_rejected_rule_1 += rejected_1
                total_rejected_rule_2 += rejected_2
                total_rejected_rule_3 += rejected_3

        logger.info(f'Process completed. Accepted sets: {total_accepted}, Rejected sets: \nrule 1: {total_rejected_rule_1}\nrule 2: {total_rejected_rule_2}\nrule 3: {total_rejected_rule_3}')
        return True
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        return None

if __name__ == "__main__":
    main()
