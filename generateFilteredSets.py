import psycopg2
from itertools import combinations
from collections import defaultdict
from psycopg2 import Error
import logging
import configparser
import psycopg2.extras
from tqdm import tqdm

logging.basicConfig(filename='logs/generateFilteredSets.log',
                    filemode='a',
                    format='%(asctime)s; %(levelname)s; %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_historical_sets():
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("SELECT draw_date, number1, number2, number3, number4, number5, number6, number7, bonus_number FROM public.lotto_max_results")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Convert each row to a tuple: (draw_date, set of numbers)
    return [(r[0], set(r[1:])) for r in rows]

def match_rule_1(candidate, winning_set):
    # Return True if candidate matches 5 or more numbers in winning_set
    return len(set(candidate) & winning_set) >= 5

def match_rule_2(candidate, winning_set):
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

def match_rule_3(candidate):
    # Return False if candidate has 4 or more consecutive numbers
    sorted_candidate = sorted(candidate)
    consecutive_count = 0
    for i in range(1, len(sorted_candidate)):
        if sorted_candidate[i] == sorted_candidate[i - 1] + 1:
            consecutive_count += 1
            if consecutive_count >= 4:
                return True
    return False

def insert_batch(batch):
    conn = connect_to_database()
    with conn.cursor() as cur:
        insert_query = """
        INSERT INTO public.filtered_lotto_sets
        (number1, number2, number3, number4, number5, number6, number7)
        VALUES %s
        ON CONFLICT DO NOTHING;
        """
        psycopg2.extras.execute_values(cur, insert_query, batch)
    conn.commit()
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
    db_config = read_db_config()
    """ Connect to the PostgreSQL database """
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except (Exception, Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        return None

def main():
    logger.info('Starting filtered set generation process.')
    try:
        historical_sets = load_historical_sets()
        logger.info(f'Loaded {len(historical_sets)} historical sets.')

        BATCH_SIZE = 1000
        batch_rejected = []
        batches_completed = 0

        number_of_accepted_sets = 0
        number_of_rejected_sets_rule_1 = 0
        number_of_rejected_sets_rule_2 = 0
        number_of_rejected_sets_rule_3 = 0

        logger.info('Starting combination generation and filtering.')
        for candidate in tqdm(combinations(range(1, 51), 7), total=99884400):
            for draw_date, winning_set in historical_sets:
                if match_rule_1(candidate, winning_set):
                    batch_rejected.append(candidate)
                    number_of_rejected_sets_rule_1 += 1
                    break  # matched one draw; no need to check others
                elif match_rule_2(candidate, winning_set):
                    batch_rejected.append(candidate)
                    number_of_rejected_sets_rule_2 += 1
                    break  # matched one draw; no need to check others
            else:
                if match_rule_3(candidate):
                    batch_rejected.append(candidate)
                    number_of_rejected_sets_rule_3 += 1
                else:
                    number_of_accepted_sets += 1
            if len(batch_rejected) >= BATCH_SIZE:
                insert_batch(batch_rejected)
                batch_rejected = []
                batches_completed += 1
                if batches_completed % 10 == 0:
                    logger.info(f'Inserted {batches_completed * BATCH_SIZE} sets so far. Rejected sets: {number_of_rejected_sets_rule_1 + number_of_rejected_sets_rule_2 + number_of_rejected_sets_rule_3}; accepted sets: {number_of_accepted_sets}')

        # Final batch
        if batch_rejected:
            insert_batch(batch_rejected)
            batches_completed += 1
            logger.info(f'Inserted final batch of {len(batch_rejected)} sets.')

        logger.info(f'Process completed. Accepted sets: {number_of_accepted_sets}, Rejected sets: \nrule 1: {number_of_rejected_sets_rule_1}\nrule 2: {number_of_rejected_sets_rule_2}\nrule 3: {number_of_rejected_sets_rule_3}')
        return True
    except Exception as e:
        logger.error(f'An error occurred: {e}')
        return None

if __name__ == "__main__":
    main()
