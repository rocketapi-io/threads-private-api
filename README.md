# threads-private-api

This repository aims to demonstrate how to use the `rocketapi` Python library to interact with the Threads API of the RocketAPI.io service. The two main functionalities provided are the ability to scrape user followers and extract thread replies from Threads. 

## Contents

1. `scrape_followers.py`: Given a username or user ID, this script extracts all subscribers (using pagination) of the user in Threads. The data is then saved to a .csv file at `var/followers/{user_id}.csv` using the pandas library.
2. `extract_thread_replies.py`: Given a thread ID, this script extracts all replies on a thread (using pagination) and saves them to a .csv file at `var/thread_replies/{thread_id}.csv` using the pandas library.

## Prerequisites

1. Python 3.7 or later.
2. [RocketAPI](https://rocketapi.io) account.
3. Installed RocketAPI Python library. You can install it with pip:

    ```
    pip install rocketapi
    ```

## Scrape Followers

https://raw.githubusercontent.com/rocketapi-io/threads-private-api/main/videos/scrape_followers_example.mp4

The `scrape_followers.py` script is used to scrape followers from a specific user on Threads, given their username or user ID as input. 

Here is an in-depth explanation of how the script works:

- The script begins by reading the `ROCKETAPI_TOKEN` from the `.env` file. This is used to authenticate the InstagramAPI and ThreadsAPI clients.

- The `get_user_info` function sends a request to InstagramAPI to retrieve user information given a username.

- The `get_user_id` function accepts either a username or user ID. If a username is provided, it uses the `get_user_info` function to retrieve the user ID. If an ID is provided, it returns the ID directly.

- The `get_followers` function sends a request to ThreadsAPI to retrieve followers of a user given their user ID and a `max_id` for pagination.

- The `scrape_followers` function is the main function that uses the functions above to scrape followers from the user and saves them into a CSV file. 

- First, it retrieves the user ID from the input value (username or user ID).

- It then enters a loop where it retrieves followers of the user, saves their details into a dataframe, and writes the dataframe to a CSV file. This loop continues until all followers have been retrieved (i.e., no more `next_max_id` in the response).

- The details saved for each follower are their user ID (`pk`), `username`, `full_name`, `is_private`, and `is_verified` status.

- The script employs the decorator `retry_on_exception` to retry failed requests to InstagramAPI and ThreadsAPI due to exceptions. It makes up to 3 attempts for each failed request.

- If Instagram returns a wrong max ID (sometimes happens and returns `"100"`), it's recognized and handled correctly by re-requesting the same page.

- The script also keeps track of the total count of followers, which is logged at the end of the script.

### Usage:

You can run the script from the command line as follows:

```bash
python scrape_followers.py <username or user_id>
```

Replace `<username or user_id>` with the username or user ID of the user whose followers you want to scrape.

The script will save the followers to a CSV file named `{user_id}.csv` in the `var/followers/` directory. Each row in the CSV file represents a follower, and the columns represent the follower's details (user ID, username, full name, whether their account is private, and whether they are verified). 

Please ensure that the `ROCKETAPI_TOKEN` in your `.env` file is set correctly to your [rocketapi.io](https://rocketapi.io/dashboard/) API token before running the script.

## Extract Thread Replies

https://raw.githubusercontent.com/rocketapi-io/threads-private-api/main/videos/extrach_thread_replies_example.mp4

The `extract_thread_replies.py` is designed to scrape replies from a specific thread on Threads using the RocketAPI. 

When the script is executed, it first fetches the required environment variable for the RocketAPI token using `load_dotenv()`. This token is used to authenticate the ThreadsAPI object, which will be used to interact with the RocketAPI. 

The main function of the script is `extract_thread_replies(thread_id)`. It takes as input the `thread_id` for the specific thread you want to scrape replies from. 

Inside this function, it initiates a `while` loop to paginate through all replies in the given thread using the `get_thread_replies()` function (which is decorated with `retry_on_exception()` to ensure robustness against API request failures). The replies are fetched in batches until no more replies are available. 

During each loop iteration, for each reply fetched, the script checks if the reply's id is already present in the existing list of fetched replies' ids. If it is, a log message is printed out, an exit flag is set, and the loop moves to the next reply. If the reply's id is not present, it is added to the list, and the relevant fields are extracted from the reply and appended to a list of dictionaries. 

The relevant fields extracted from each reply are as follows:

- `id`: the id of the reply
- `thread_type`: the type of the thread
- `user_pk`: the user's pk (id)
- `username`: the user's username
- `full_name`: the user's full name
- `caption_text`: the text of the caption (if available)
- `like_count`: the count of likes
- `taken_at`: the time when the reply was made

After all replies in a batch are processed, they are saved into a DataFrame and then exported to a CSV file in the `var/thread_replies/` directory. The filename is the `thread_id` value. This process repeats until no more new replies are available or a duplicate reply id is encountered.

If the exit flag is set due to encountering a duplicate reply id, the while loop is broken and the script finishes its execution.


### Usage

You can run the script from the command line as follows:

```bash
python extract_thread_replies.py <thread_id>
```

You must provide the `thread_id` as an argument when running the script. The `thread_id` is an identifier for the specific thread you want to scrape replies from.

Please ensure that the `ROCKETAPI_TOKEN` in your `.env` file is set correctly to your [rocketapi.io](https://rocketapi.io/dashboard/) API token before running the script.

## Documentation

The RocketAPI documentation is available [here](https://docs.rocketapi.io/category/threads). It provides detailed information about the Threads API, which these scripts use to fetch followers and thread replies.

## Contributing

Contributions are welcome! Please fork this repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See `LICENSE` for more details.

## Acknowledgements

This project uses the [RocketAPI](https://rocketapi.io) service and its Python library [rocketapi](https://pypi.org/project/rocketapi/) for interacting with the Threads API.
