# Rekognize Twitter API Client

Rekognize is a Python Twitter REST API client for accessing Twitter data. 


## Installation

Install `rekognize` from [PyPI](https://pypi.org/project/rekognize/).

```
pip install rekognize
```

> Before you get started, you will need to [authorize](https://rekognize.io/twitter/auth/) Rekognize Twitter application to obtain your `ACCESS_TOKEN` and `ACCESS_TOKEN_SECRET`.


## Usage

Import client and initialize it:

```python
from rekognize.twitter import UserClient

ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
ACCESS_TOKEN_SECRET = 'YOUR_ACCESS_TOKEN_SECRET'

client = UserClient(
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET
)
```

Then you can access [Twitter REST API endpoints](https://developer.twitter.com/en/docs/api-reference-index) as follows:

```python
# trends/available
client.api.trends.available.get()

# users/search
client.api.users.search.get(
    q='#TwitterAPI',
    count=100,
)

# users/lookup
r = client.api.users.lookup.post(
    screen_name='twitter',
)

client.api.users.show.get(screen_name='twitter')
```

Alternatively, calls can be written in the following syntax:

```python
response = client.api['users/show'].get(screen_name='twitter')
```

`rekognize` is a read-only API. You can use it to access every `GET` endpoint of the [Twitter REST API](https://developer.twitter.com/en/docs/api-reference-index). Twitter API conditions such as the request parameter syntax and rate limits apply. 


### Response

Calls to REST API return an `ApiResponse` object, which in addition to returned data, also gives you access to the remaining number of calls to the same endpoint (reset every 15 mins), response headers and the resource URL.

```python
response.data           # decoded JSON data
response.resource_url   # resource URL
response.remaining      # remaining number of calls you can make to the same API endpoint; reset every 15 mins
response.headers        # dictionary containing response HTTP headers
```


## Exceptions

There are 4 types of exceptions in `birdy` all subclasses of base `BirdyException` (which is never directly raised).

  - `TwitterClientError` raised for connection and access token retrieval errors
  - `TwitterApiError` raised when Twitter returns an error
  - `TwitterAuthError` raised when authentication fails,
    `TwitterApiError` subclass
  - `TwitterRateLimitError` raised when rate limit for resource is reached, `TwitterApiError` subclass

