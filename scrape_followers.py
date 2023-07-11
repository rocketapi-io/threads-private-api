import os
import sys
import pandas as pd
import logging
from dotenv import load_dotenv
from rocketapi import InstagramAPI, ThreadsAPI
from decorators import retry_on_exception


logging.basicConfig(level=logging.INFO)
load_dotenv()
token = os.getenv('ROCKETAPI_TOKEN')

ig_api = InstagramAPI(token)
threads_api = ThreadsAPI(token)


@retry_on_exception(max_tries=3)
def get_user_info(username):
    return ig_api.get_user_info(username)


def get_user_id(input_value):
    try:
        int(input_value)
        return input_value
    except ValueError:
        res = get_user_info(input_value)
        return res['data']['user']['id']


@retry_on_exception(max_tries=3)
def get_followers(user_id, max_id=None):
    return threads_api.get_user_followers(user_id, max_id)


def scrape_followers(input_value):
    user_id = get_user_id(input_value)
    if not user_id:
        logging.error(f"Failed to get user_id for {input_value}")
        return

    logging.info(f"Scraping followers for user_id: {user_id}")
    next_max_id = None
    followers_data = []
    followers_count = None
    first_100 = False  # avoiding traps

    fn = f"var/followers/{user_id}.csv"
    while True:
        res = get_followers(user_id, next_max_id)
        if not res or not res.get('next_max_id'):
            break

        if res.get('next_max_id') == "100":
            if first_100:
                logging.info("Instagram returns wrong max id, try again")
                continue
            first_100 = True

        if not followers_count:
            followers_count = res['user_count']
            logging.info(f"Total followers: {followers_count}")

        followers = res['users']
        next_max_id = res['next_max_id']
        logging.info(f"Got {len(followers)} followers, next_max_id: {next_max_id}")

        for follower in followers:
            data = {
                "pk": follower['pk'],
                "username": follower['username'],
                "full_name": follower['full_name'],
                "is_private": follower['is_private'],
                "is_verified": follower['is_verified'],
            }
            followers_data.append(data)

        df = pd.DataFrame(followers_data)
        df.to_csv(fn, index=False)

    logging.info(f"Done scraping followers for user_id: {user_id}")
    logging.info(f"Total followers: {followers_count}")
    logging.info(f"Saved to: {fn}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scrape_followers.py <username or user_id>")
        return
    input_value = sys.argv[1]
    scrape_followers(input_value)


if __name__ == "__main__":
    main()
