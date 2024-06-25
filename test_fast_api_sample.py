import pytest
from fastapi.testclient import TestClient
from fast_api_sample import app, BookStore, Book, BOOKS_FILE
import json
import os

client = TestClient(app)

def setup_module():
    # Create a temporary books.json file for testing
    os.makedirs("tests", exist_ok=True)
    with open("tests/books.json", "w") as f:
        json.dump([], f)
    global bookstore
    bookstore = BookStore("tests/books.json")

def teardown_module():
    # Remove the temporary books.json file
    os.remove("tests/books.json")

# Test cases for get_all_books
def test_get_all_books_empty():
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []

def test_get_all_books_populated():
    bookstore.add_book(Book(name="Book 1", genre="fiction", price=10.0))
    bookstore.add_book(Book(name="Book 2", genre="romance", price=15.0))
    response = client.get("/books")
    assert response.status_code == 200
    assert len(response.json()) == 2

# Test cases for get_book_by_id
def test_get_book_by_id_valid():
    book_id = bookstore.add_book(Book(name="Book 1", genre="fiction", price=10.0))["book-id"]
    response = client.get(f"/book-by-id?book_id={book_id}")
    assert response.status_code == 200
    assert response.json()["book_id"] == book_id

def test_get_book_by_id_invalid():
    response = client.get("/book-by-id?book_id=invalid_id")
    assert response.status_code == 404

# Test cases for get_book_by_index
def test_get_book_by_index_valid():
    bookstore.add_book(Book(name="Book 1", genre="fiction", price=10.0))
    bookstore.add_book(Book(name="Book 2", genre="romance", price=15.0))
    response = client.get("/books-by-index/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Book 2"

def test_get_book_by_index_out_of_range():
    response = client.get("/books-by-index/10")
    assert response.status_code == 404

# Test cases for add_book
def test_add_book_valid():
    book_data = {"name": "Book 1", "genre": "fiction", "price": 10.0}
    response = client.post("/add-book", json=book_data)
    assert response.status_code == 200
    assert "book-id" in response.json()

def test_add_book_invalid_genre():
    book_data = {"name": "Book 1", "genre": "invalid_genre", "price": 10.0}
    response = client.post("/add-book", json=book_data)
    assert response.status_code == 422

# Test cases for update_book
def test_update_book_valid():
    book_id = bookstore.add_book(Book(name="Book 1", genre="fiction", price=10.0))["book-id"]
    update_book_data = {"name": "Updated Book 1", "genre": "romance", "price": 15.0}
    response = client.post(f"/update-book/{book_id}", json=update_book_data)
    assert response.status_code == 200
    assert response.json()["book"]["name"] == "Updated Book 1"

def test_update_book_invalid_id():
    update_book_data = {"name": "Updated Book 1", "genre": "romance", "price": 15.0}
    response = client.post("/update-book/invalid_id", json=update_book_data)
    assert response.status_code == 404

# Test cases for delete_book
def test_delete_book_valid():
    book_id = bookstore.add_book(Book(name="Book 1", genre="fiction", price=10.0))["book-id"]
    response = client.delete(f"/delete-book?book_id={book_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "The book has been deleted"

def test_delete_book_invalid_id():
    response = client.delete("/delete-book?book_id=invalid_id")
    assert response.status_code == 404

# Test cases for random_book
def test_random_book():
    bookstore.add_book(Book(name="Book 1", genre="fiction", price=10.0))
    bookstore.add_book(Book(name="Book 2", genre="romance", price=15.0))
    response = client.get("/random-book")
    assert response.status_code == 200
    assert response.json()["name"] in ["Book 1", "Book 2"]

# Test cases for hello_world
def test_hello_world():
    response = client.get("/hello-world")
    assert response.status_code == 200
    assert response.json() == {"messages": "HELLO World!"}

# Test cases for root
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"messages": "Welcome to the bookstore"}