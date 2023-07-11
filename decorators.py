import logging
from rocketapi.exceptions import NotFoundException, BadResponseException


logging.basicConfig(level=logging.INFO)


def retry_on_exception(max_tries=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except (NotFoundException, BadResponseException):
                    if i < max_tries - 1:
                        logging.warning(f"Attempt {i + 1} of {max_tries} failed. Retrying...")
                        continue
                    else:
                        logging.error(f"Attempt {i + 1} of {max_tries} failed. Aborting...")
                        return None
                except Exception as e:
                    logging.warning(f"An unexpected error occurred: {e}")
                    if i < max_tries - 1:
                        logging.warning(f"Attempt {i + 1} of {max_tries} failed. Retrying...")
                        continue
                    else:
                        logging.error(f"Attempt {i + 1} of {max_tries} failed. Aborting...")
                        return None
        return wrapper
    return decorator
