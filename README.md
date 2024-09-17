
# Message API
This is a simple Python implementation of a REST-API for sending and receiving messages. The API is implemented using the FastAPI framework.

## API Documentation
The API has four endpoints:

### POST /v1/message: Send a message to a user

The body of the request should contain the following parameters:
- **sender**: The sender of the message
- **recipient**: The recipient of the message
- **content**: The message to be sent

### GET /v1/message/{user}: Retrieve messages for a user

The parameter `user` is the user whose messages are to be retrieved. Some optional query parameters can be used to filter the messages:

- **offset**: The number of messages to skip (default `0`)
- **limit**: The maximum number of messages to retrieve (default `100`, max `500`)
- **only_new**: If set to `true`, only new messages will be retrieved (default `false`)

The response will contain a list of messages ordered by the time they were sent in descending order. 

Each message will contain the following fields:
- **id**: The unique identifier of the message
- **sender**: The sender of the message
- **recipient**: The recipient of the message
- **content**: The message content
- **time_sent**: The time the message was sent
- **fetched**: A boolean indicating if the message has previously been fetched by the recipient

### POST /v1/message/delete: Delete multiple messages

The body of the request should contain the following parameter:
- **ids**: A comma-separated list of message IDs to be deleted

The response will contain the number of IDs that were successfully deleted.

### DELETE /v1/message/{id}: Delete a single message

The parameter `id` is the unique identifier of the message to be deleted.

On successful deletion, the response will not contain any content.

For more information on the endpoints and their parameters, please see the documentation at http://127.0.0.1:8000/docs (dev mode) or http://0.0.0.0:8000/docs (run mode) when running the API.


## Running the API

To run the API, Python needs to be installed on the computer and the required packages needed for running the project can be found in the [requirements.txt](src/requirements.txt) file. To install the required packages, run the following command in the terminal:

```bash
pip install -r path/to/requirements.txt
```

To run the API (hosting it locally), navigate to the `src` directory and run the following command in the terminal:

```bash
fastapi run main.py
```

or to run in development mode:

```bash
fastapi dev main.py
```

An SQLite database is used to store the messages and will be initialized when the API is run for the first time.

## Tests

The file [test_main.py](src/test_main.py) contains some unit tests for the API. To run the tests, run the following command in the terminal:

```bash
pytest
```
The results of the tests are displayed in the terminal.

The functionality of the API can also be tested in the documentation at http://127.0.0.1:8000/docs (dev mode) or http://0.0.0.0:8000/docs (run mode).