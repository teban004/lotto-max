import psycopg2
from itertools import combinations
from psycopg2 import Error
import logging
import psycopg2.extras
import os
from dotenv import load_dotenv
from typing import List, Tuple
from multiprocessing import Manager, Pool
import math

load_dotenv()

logging.basicConfig(filename='logs/generateFilteredSets.log',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

TOTAL_COMBINATIONS = 99884400
NUM_WORKERS = 3
MAX_DB_INSERT_BATCH = 1000  # Maximum number of sets to insert in one batch
WORK_CHUNK_SIZE = 100000  # Size of each chunk for processing

def validate_env_vars():
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"Missing required environment variable: {var}")
            raise EnvironmentError(f"Missing required environment variable: {var}")

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
    temp_set = winning_set.copy()  # Use a copy to avoid modifying the original set
    for num in candidate:
        if num in temp_set:
            count += 1
            temp_set.remove(num)  # Avoid double counting
        elif (num - 1 in temp_set) or (num + 1 in temp_set):
            count += 1
            temp_set.remove(num - 1 if (num - 1 in temp_set) else num + 1)
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
    conn = None
    try:
        conn = connect_to_database()
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
        if conn:
            conn.close()

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
        raise

def process_chunk(chunk_range, historical_sets):
    """Process a smaller chunk of combinations."""
    start, end = chunk_range
    batch_rejected = []
    number_of_accepted_sets = 0
    number_of_rejected_sets_rule_1 = 0
    number_of_rejected_sets_rule_2 = 0
    number_of_rejected_sets_rule_3 = 0

    logger.info(f"Processing chunk: {start} to {end}")
    processed_count = 0
    for candidate in combinations(range(1, 51), 7):
        if start <= hash(candidate) % TOTAL_COMBINATIONS < end:
            processed_count += 1
            if processed_count % 10000 == 0:
                logger.info(f"Chunk {start}-{end}: Processed {processed_count} combinations so far.")
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

    logger.info(f"Finished chunk: {start} to {end}. Accepted: {number_of_accepted_sets}, Rejected: {len(batch_rejected)}")
    return batch_rejected, number_of_accepted_sets, number_of_rejected_sets_rule_1, number_of_rejected_sets_rule_2, number_of_rejected_sets_rule_3

def main():
    logger.info('Starting filtered set generation process.')
    try:
        validate_env_vars()
        historical_sets = load_historical_sets()
        logger.info(f'Loaded {len(historical_sets)} historical sets.')

        total_chunks = math.ceil(TOTAL_COMBINATIONS / WORK_CHUNK_SIZE)
        chunk_ranges = [(i * WORK_CHUNK_SIZE, min((i + 1) * WORK_CHUNK_SIZE, TOTAL_COMBINATIONS)) for i in range(total_chunks)]

        total_accepted = 0
        total_rejected_rule_1 = 0
        total_rejected_rule_2 = 0
        total_rejected_rule_3 = 0

        # Use multiprocessing to dynamically assign chunks to workers
        with Pool(processes=NUM_WORKERS) as pool:
            results = [pool.apply_async(process_chunk, args=(chunk, historical_sets)) for chunk in chunk_ranges]

            for result in results:
                batch_rejected, accepted, rejected_1, rejected_2, rejected_3 = result.get()
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
