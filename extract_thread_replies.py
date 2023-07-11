import os
import sys
import pandas as pd
import logging
from dotenv import load_dotenv
from rocketapi import ThreadsAPI
from decorators import retry_on_exception


logging.basicConfig(level=logging.INFO)
load_dotenv()
token = os.getenv('ROCKETAPI_TOKEN')
threads_api = ThreadsAPI(token)


@retry_on_exception(max_tries=3)
def get_thread_replies(thread_id, max_id=None):
    return threads_api.get_thread_replies(thread_id, max_id)


def extract_thread_replies(thread_id):
    if not thread_id:
        logging.error(f"Invalid thread_id: {thread_id}")
        return

    logging.info(f"Extracting replies for thread_id: {thread_id}")
    next_max_id = None
    replies_data = []
    replies_count = None
    replies_ids = set()
    exit_flag = False

    fn = f"var/thread_replies/{thread_id}.csv"
    while True:
        res = get_thread_replies(thread_id, next_max_id)
        if not res or not res.get('paging_tokens', {}).get('downwards'):
            break

        if not replies_count:
            replies_count = res['containing_thread']['thread_items'][0]['post']['text_post_app_info']['direct_reply_count']
            logging.info(f"Total replies: {replies_count}")

        next_max_id = res['paging_tokens']['downwards']
        logging.info(f"Got {len(res['reply_threads'])} replies, next_max_id: {next_max_id}")

        for reply in res['reply_threads']:
            if reply['id'] in replies_ids:
                logging.info(f"Fetched duplicate reply: {reply['id']}")
                exit_flag = True
                continue
            replies_ids.add(reply['id'])
            if not reply.get('posts') or not reply['posts']:
                logging.info(f"Skip empty reply: {reply['id']}")
                continue
            post = reply['posts'][0]
            data = {
                "id": reply['id'],
                "thread_type": reply['thread_type'],
                "user_pk": post['user']['pk'],
                "username": post['user']['username'],
                "full_name": post['user']['full_name'],
                "caption_text": post['caption']['text'] if post.get('caption') else '',
                "like_count": post['like_count'],
                "taken_at": post['taken_at'],
            }
            replies_data.append(data)

        df = pd.DataFrame(replies_data)
        df.to_csv(fn, index=False)

        if exit_flag:
            break

    logging.info(f"Done extracting replies for thread_id: {thread_id}")
    logging.info(f"Saved to: {fn}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_thread_replies.py <thread_id>")
        return
    thread_id = sys.argv[1]
    extract_thread_replies(thread_id)


if __name__ == "__main__":
    main()
