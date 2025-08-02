import sys
import json
from pathlib import \
    Path  # Importing the 'Path' class from the 'pathlib' module
from time import sleep  # Importing the 'sleep' function from the 'time' module
from urllib.parse import \
    unquote  # Importing the 'unquote' function from the 'urllib.parse' module

from requests import \
    get  # Importing the 'get' function from the 'requests' module

token = get("https://opentdb.com/api_token.php?command=request").json()[
    "token"
]  # Sending a GET request to obtain an API token from a URL and extracting the token value from the JSON response
arg_category_start = ( 0 )
if len(sys.argv) > 1:
    arg_category_start = int(sys.argv[1])
num = (
    9 + arg_category_start # Assigning the value 9 to the variable 'num' (the first trivia category number)
)
count = 50  # Assigning the value 50 to the variable 'count'
questions_written = 0  # Assigning the value 0 to the variable 'questions_written'
to_save = []

while 1:  # Starting an infinite loop
    current = get(f"https://opentdb.com/api_category.php").json()["trivia_categories"][
        num - 9
    ][
        "name"
    ]  # Sending a GET request to obtain the current trivia category name from a URL and extracting it from the JSON response

    file_path = Path(
        f"{unquote(current)}.json"
    ).touch()  # Creating a new file with the name of the current trivia category, URL decoding the category name and appending '.json' extension

    full_count = get(f"https://opentdb.com/api_count.php?category={num}").json()[
        "category_question_count"
    ][
        "total_question_count"
    ]  # Sending a GET request to obtain the total question count for the current trivia category from a URL and extracting it from the JSON response

    left_count = (
        full_count - questions_written
    )  # Calculating the number of questions remaining for the current trivia category

    print(
        f"{left_count} questions left in {unquote(current)}, number {num - 9}"
    )  # Printing the number of questions remaining for the current trivia category

    if (
        count > left_count
    ):  # If the desired question count is greater than the remaining question count
        count = (
            left_count  # Set the desired question count to the remaining question count
        )

    data = get(  # Send a GET request to the Open Trivia Database API
        "https://opentdb.com/api.php?amount={}&category={}&encode=url3986&token={}".format(
            count,
            num,
            token,  # Format the URL with the desired question count, category number, and API token
        )
    ).json()  # Convert the API response to JSON

    results = data["results"]
    if len(results) > 0:
        print(  # Print a success message
            f"Successfully retrieved {len(data['results'])} questions to {unquote(current)}.json. Total questions: {questions_written + len(data['results'])}"
        )
        to_save.extend(results)
        questions_written += (
            count  # Increment the total question count by the desired question count
        )
        if (
            questions_written > full_count
        ):  # If the total question count is greater than or equal to the full question count
            print("BUG in logic. Ignore this")
        sleep(
            5.01
        )  # Pause the execution of the program for a little over 5 seconds (to avoid exceeding the API request limit)
    else:  # If the API response does not contain a 'results' field
        for question in to_save:
            for key, value in question.items():
                if isinstance(value, str):
                    question[key] = unquote(value)
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, str):
                            question[key][i] = unquote(item)


        with open(
            f"{unquote(current)}.json", "w", newline=""
        ) as file:  # Open the current category's CSV file in append mode
            json.dump(to_save, file, indent=4)

        print("Wrote to file")

        num += 1  # Increment the category number
        to_save = []

        count = 50  # Reset the desired question count to 50
        current_count = 0

        if num == 33:  # If the category number is 33
            print("Done!")  # Print a completion message

            break  # Break the loop
        questions_written = 0  # Reset the total question count

        sleep(
            5.01
        )  # Pause the execution of the program for a little over 5 seconds (to avoid exceeding the API request limit)
