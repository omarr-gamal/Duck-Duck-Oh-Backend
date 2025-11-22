# Duck-Duck-Oh

This project is a simple search engine API that allows you to add and search through a collection of documents. Check out a frontend React app that integrates with this API at [Omar-Gebal/react-simple-search-engine](https://github.com/Omar-Gebal/react-simple-search-engine/).

## Engine Capabilities

This search engine uses the following techniques:

- **Tokenization:** The search engine tokenizes the documents into words after removing any HTML tags and punctuation. It also removes any stop words, which are words that are commonly used in the English language but do not add any meaning to the document. For example, the words "the", "a", and "is" are stop words.

- **TF-IDF Vectorization:** The search engine uses the TF-IDF vectorization technique to rank the documents by relevance. The TF-IDF algorithm takes into account the frequency of a word in a document and the number of documents that contain the word. The more frequently a word appears in a document, the more important it is. The more documents that contain the word, the less important it is.

- **Ranking:** The search engine ranks the results by calculating the cosine similarity between the search term and the documents. To do this, it first converts the search term and the document bodies into numerical vectors using the TF-IDF vectorizer. The vectorizer converts the search term and document bodies into a sparse matrix, where each row represents a document and each column represents a word. Each cell in the matrix represents the importance of a word in a document, based on the frequency of the word in the document and the rarity of the word in the entire collection of documents. Next, the search engine calculates the cosine similarity between the search vector and each document vector. The cosine similarity is a measure of similarity between two non-zero vectors of an inner product space that measures the cosine of the angle between them.

- **Spell Checking:** The search engine spell checks the search queries by using the Levenshtein distance algorithm which calculates the number of edits required to transform one word into another and suggest the most likely word that the user meant to search for.

- **Stemming:** The search engine uses the Porter stemmer algorithm to stem the words in the documents. This algorithm removes the suffixes from the words to get the root word. For example, the words "running", "ran", and "run" will all be stemmed to "run".

## Engine Features

This search engine supports the following features:

- **Add documents** to the search engine via a POST request to the `/documents` endpoint. The request should include a `body` field in the JSON payload, which should contain the HTML body of the document.

- **Search for documents** that contain a given search term by making a GET request to the `/search` endpoint. This endpoint requires a `query` parameter in the query string, which should contain the search term. The search engine will return a list of documents that contain the search term, ranked by relevance.

- **Search for images** by making a GET request to the `/search/images` endpoint. This endpoint requires a `query` parameter in the query string, which should contain the search term. The search engine will return a list of images and the document that contains the image, ranked by relevance.

- The search engine includes a **spell checker** that will automatically correct any misspellings in the search term. To disable this feature, include a `no_spell_check` parameter with a value of `true` in the query string of the `/search` endpoint.

- The search engine returns a results of a list of objects, or documents, containing the following fields: `id`, `title`, `body`, `added_at`, and `outline`.

## Rate Limiting & Authentication

The API implements rate limiting:

- **Unauthenticated Requests:** Limited to **10 requests per minute**.
- **Authenticated Requests:** Limited to **20 requests per minute**.

You can generate an API key and include it in your requests using the `X-API-KEY` header.

### Generating an API Key

Send a POST request to `/api/keys` with an optional description.

### Using an API Key

Include the key in the `X-API-KEY` header:

```bash
curl -H "X-API-KEY: your_api_key_here" http://localhost:5000/search?query=example
```

## Setup

To set up the search engine, follow these steps:

1. Clone the repository and navigate to the project directory.

2. Configure environment variables:

You mainly need to set database url and credentials. You provide a connection string as a whole or set the fields individually. The [.env.example](.env.example) file contains documentation for the environment variables used by the app.

You can also configure rate limits using the following environment variables:
- `RATELIMIT_GUEST`: Rate limit for unauthenticated requests (default: "10 per minute")
- `RATELIMIT_AUTHENTICATED`: Rate limit for authenticated requests (default: "20 per minute")

```bash
cp .env.example .env 
vi .env # set db connection string.
```

3. Build a Docker image:

```bash
docker build -t duck-duck-oh-backend .
```

4. Run the app as a container:

The api listens on port `5000` 

```bash
docker run -d -p 5000:5000 duck-duck-oh-backend
```

5. Access the search engine  at <http://localhost:5000>.

6. Access API documentation at <http://localhost:5000/docs> to view and interact with the API endpoints. Here's a preview of the documentation:
  <img width="1920" height="950" alt="Screenshot 2025-11-21 at 20-37-07 Duck Duck Oh API 1 0" src="https://github.com/user-attachments/assets/52172304-29af-4808-bd35-106f18c0c786" />
 
### Running Tests

**Run all tests:**
```bash
pytest -v
```

**Run a specific test file:**
```bash
pytest tests/test_engine.py
pytest tests/test_models.py
pytest tests/test_routes.py
```

**Run tests matching a pattern:**
```bash
pytest -k "search"
```

### Coverage Reports

**Generate HTML coverage report with missing lines:**
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

This creates a `htmlcov/` directory. Open `htmlcov/index.html` in your browser to view the interactive coverage report.


## Endpoints

### POST /documents

Adds a new document to the search engine.

#### Request

```json
{
  "body": "<html>...</html>"
}
```

#### Response

```json
{
  "success": true
}
```

### GET /documents/<document_id>

Gets a document with the given ID.

#### Response

```json
{
    "success": true,
    "document": {
        "id": 1,
        "title": "Example Document",
        "body": "<html>...</html>",
        "added_at": "2022-12-25 01:33:45"
    }
}
```

### GET /search

This route is used to search the documents in the database. It takes in a single query parameter, `query`, which is the search term. It also takes in an optional boolean parameter, `no_spell_check`, which determines whether to perform spell checking on the search term.

#### Request

```txt
/search?query=example
```

#### Response

```json
{
    "success": true,
    "results": [
        {
            "id": 1,
            "title": "Example Document",
            "body": "<html>...</html>",
            "added_at": "2022-12-25 01:33:45",
            "outline": "This is an example document. It contains the word example."
        }
    ],
    "query": "example"
}
```

### POST /api/keys

Generates a new API key.

#### Request

```json
{
  "description": "My App Key"
}
```

#### Response

```json
{
  "api_key": {
    "key": "generated_secret_key",
    "description": "My App Key",
    "created_at": "2025-11-22T20:00:00"
  }
}
```

Note: The `outline` field is a snippet of the document that is supposed to contain the search term, however, it returns a random snipet at the moment which should be modified in the future.

Note: The `query` field is the search term that was actually used to search the documents since it may differ from the original search term if the spell checker was used.

## License

MIT, do as you please.

