### API Endpoint

`GET /v1/get_concurrent_calls`

**Query Parameters:**
- `userKey` (required): The user key to access call records from the call records API endpoint.

### Response

The API will return a JSON response with the following structure:

```json
{
    "results": [
        {
            "customerId": "<customer_id>",
            "date": "<YYYY-MM-DD>",
            "maxConcurrentCalls": <max_concurrent_calls>,
            "timestamp": <timestamp_of_max_concurrency>,
            "callIds": [<call_id_1>, <call_id_2>, ...]
        }
    ]
}
```

### Steps to Run the Flask Server

1. **Install Dependencies:**
   Make sure you have Python 3.8+ installed. Create a virtual environment and install the necessary dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the Flask Server:**
   ```bash
   flask run
   ```
   The server will start on `http://127.0.0.1:5000`.

3. **GET the result from the result API:**
   You can use `curl`, Postman, or a browser to test the endpoint:
   ```bash
   curl "http://127.0.0.1:5000/v1/get_concurrent_calls?userKey=<your_user_key>"
   ```
