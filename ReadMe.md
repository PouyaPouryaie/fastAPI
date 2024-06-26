# Summary
This code defines a FastAPI application that manages a bookstore. It uses a JSON file to store book data and provides endpoints for various operations. The `Book` class defines the structure of a book object, including its name, genre, price, and a unique ID. The application offers endpoints for retrieving a random book, listing all books, getting a book by index, adding a new book, updating an existing book, retrieving a book by its ID, and deleting a book. Each endpoint handles requests, interacts with the book data, and returns appropriate responses, including error handling for invalid requests. 

# details (summary writer)
This code creates a simple bookstore application using FastAPI, a Python framework for building web APIs. It allows users to manage a collection of books through various API endpoints.

**Here's a breakdown of how it works:**

1. **Data Model:** The `Book` class defines the structure of a book, including its name, genre, price, and a unique ID.

2. **BookStore Class:** This class manages the book data. It loads books from a JSON file (`books.json`) and provides methods to:
   - **Get all books:** `get_all_books()`
   - **Get a book by ID:** `get_book_by_id()`
   - **Get a book by index:** `get_book_by_index()`
   - **Add a new book:** `add_book()`
   - **Update an existing book:** `update_book()`
   - **Delete a book:** `delete_book()`

3. **API Endpoints:** The code defines various API endpoints using FastAPI's decorators:
   - **`/hello-world`:** Returns a simple greeting message.
   - **`/`:** Returns a welcome message to the bookstore.
   - **`/random-book`:** Returns a random book from the collection.
   - **`/books`:** Returns a list of all books.
   - **`/books-by-index/{index}`:** Returns a book at a specific index in the list.
   - **`/add-book`:** Adds a new book to the collection.
   - **`/update-book/{book_id}`:** Updates an existing book by its ID.
   - **`/book-by-id`:** Returns a book by its ID.
   - **`/delete-book`:** Deletes a book by its ID.

**How the files interact:**

- The `books.json` file stores the book data in a JSON format.
- The `BookStore` class reads and writes data to this file.
- The FastAPI application uses the `BookStore` class to handle book-related requests and responses.

**In essence, this code creates a web API that allows users to interact with a bookstore database. Users can retrieve books, add new books, update existing books, and delete books using various API endpoints.**


# Requirments
1) fastapi
2) uvicorn

# To run live server locally
```shell
uvicorn fast_api_sample:app --reload
```

```shell
fastapi dev fast_api_sample.py
```

# Server default
 Serving at: http://127.0.0.1:8000  
 API docs: http://127.0.0.1:8000/docs  


# Deploy on AWS EC2
1. create EC2 Instance with these specification
   
   - ubuntu instance - t2 micro
   - key pair for connect through ssh
   - network setting with open http, https, and ssh
2. connect with ssh to instance
3. run these scripts
```shell
   sudo apt-get update
   sudo apt install -y python3-pip nginx python3-venv
```
4. config nginx to redirect external request to fastAPI app

   - you can check .fastapi_nginx file
   - you need to define that config in `/etc/nginx/sites_enabled`
   - restart nginx service after config
5. define a virtual environment and install requirements based on requirements.txt file
   - `python -m pip install -r requirements.txt`
6. run FastAPI app
   - `fastapi dev fast_api_sample.py`


# Deploy on AWSLambda
1. at first use mangum in the project and set the handler in your main file
2. create requirements.txt file based on lib in your env
   - `python -m pip freeze > requirements.txt`
   - **you can remove unnecessary lib from `requirements.txt` after that file is created**
3. build a package which name is **lib**, contains all the dependecies to upload on lambda function
   - `python -m pip install -t lib -r requirements.txt`
4. create a zip folder containing the **lib** folder and then update it by adding fast_api_sample to the zip folder
   - `(cd lib; zip ../lambda_fastapi.zip -r .)`
   - `zip lambda_fastapi.zip -u fast_api_sample.py`
5. go to the AWS Lambda and create a function with these config
   - choose python as Runtime
   - enable function url
   - choose NONE for Auth Type
   - checked the configuration for CORS
6. then upload the zip file **`(lambda_fastapi.zip)`**
7. edit Handler of lambda function wiht the handler that define in your script
   - eg: `fast_api_sample.handler`
8. click on function URL link and test your app


# Other command

1. check s3 bucket -> `aws s3 ls`
2. create bucket -> `aws s3 mb s3://fast-api-storage --region us-east-1`
