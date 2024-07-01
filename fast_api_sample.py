from fastapi import FastAPI, HTTPException, Path
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Literal, Optional
from uuid import uuid4
from mangum import Mangum
import os
import json
import random
import boto3
import botocore

BOOKS_FILE = "books.json"

app = FastAPI()
handler = Mangum(app)

# To inherit from Base Model which is used to serialize and deserialize object to Json and vice versa
class Book(BaseModel):
    """
    Represents a book with its attributes.

    Attributes:
        name (str): The name of the book.
        genre (Literal["fiction", "romance", "comedy", "adventure", "self-improvement", "drama"]): The genre of the book.
        price (float): The price of the book.
        book_id (Optional[str]): The unique identifier of the book. Defaults to a randomly generated UUID.
    """
    name: str
    genre: Literal["fiction", "romance", "comedy", "adventure", "self-improvement", "drama"]
    price: float
    book_id: Optional[str] = uuid4().hex

    def to_dict(self):
        """
        Converts the Book object to a dictionary representation.

        Returns:
            dict: A dictionary containing the book's attributes.
        """
        return {
            "name": self.name,
            "genre": self.genre,
            "price": self.price,
            "book_id": self.book_id
        }

class BookStore:
    """
    Manages a collection of books stored in a JSON file.

    Attributes:
        book_file (str): The path to the JSON file containing the book data.
        books (dict): A dictionary storing the books, keyed by their book_id.
    """
    def __init__(self, book_file:str):
        """
        Initializes the BookStore with the specified book file.

        Args:
            book_file (str): The path to the JSON file containing the book data.
        """
        self.book_file = book_file
        self.books = self._load_books()
    
    def _load_books(self):
        """
        Loads books from the JSON file into the books dictionary.

        Returns:
            dict: A dictionary containing the loaded books.
        """
        books = {}

        s3 = boto3.client("s3")

        try:
            s3.head_object(Bucket="fast-api-storage", Key=self.book_file)
            print(f"Key: '{self.book_file}' found!")
            s3_clientobj = s3.get_object(Bucket='fast-api-storage', Key=self.book_file)
            s3_clientdata = s3_clientobj['Body'].read().decode('utf-8')
            data = json.loads(s3_clientdata)

            for book_data in data:
                book = Book(
                    name=book_data["name"],
                    genre=book_data["genre"],
                    price=book_data["price"],
                    book_id=book_data["book_id"]
                )
                books[book.book_id] = book
            
            return books


        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print(f"Key: '{self.book_file}' does not exist!")
                return books
            else:
                print("Something else went wrong")
                raise

        # if os.path.exists(self.book_file):
        #     with open(self.book_file, 'r') as f:
        #         data = json.load(f)

        #         # s3.put_object(
        #         #     Bucket="fast-api-storage",
        #         #     Key=self.book_file,
        #         #     Body=json.dumps(data)
        #         # )

        #         for book_data in data:
        #             book = Book(
        #                 name=book_data["name"],
        #                 genre=book_data["genre"],
        #                 price=book_data["price"],
        #                 book_id=book_data["book_id"]
        #             )
        #             books[book.book_id] = book
        # return books


    def get_all_books(self):
        """
        Returns a list of all books in the bookstore.

        Returns:
            list: A list of Book objects.
        """
        return list(self.books.values())
    
    def get_book_by_id(self, book_id:str):
        """
        Retrieves a book by its ID.

        Args:
            book_id (str): The ID of the book to retrieve.

        Returns:
            dict: A dictionary representation of the book.

        Raises:
            HTTPException: If the book with the given ID is not found.
        """
        
        if book_id in self.books:
            return self.books[book_id].to_dict()
        else:
            raise HTTPException(404, f"Book ID {book_id} not found in database.")

    def get_book_by_index(self, index: int):
        """
        Retrieves a book by its index in the bookstore.

        Args:
            index (int): The index of the book to retrieve.

        Returns:
            dict: A dictionary representation of the book.

        Raises:
            HTTPException: If the index is out of range.
        """
        if 0 <= index < len(self.books):
            return list(self.books.values())[index].to_dict() 
        else:
            raise HTTPException(status_code=404, detail=f"book index {index} out of range ({len(self.books)})")

    def add_book(self, book: Book):
        """
        Adds a new book to the bookstore.

        Args:
            book (Book): The book object to add.

        Returns:
            dict: A dictionary containing the book's ID.
        """
        book.book_id = uuid4().hex
        self.books[book.book_id] = book
        self._save_books()
        return {"book-id": book.book_id}
    
    def update_book(self, book_id: str, update_book: Book):
        """
        Updates an existing book in the bookstore.

        Args:
            book_id (str): The ID of the book to update.
            update_book (Book): The updated book object.

        Returns:
            dict: A dictionary containing the updated book and its ID.

        Raises:
            HTTPException: If the book with the given ID is not found.
        """
        if book_id in self.books:
            self.books[book_id] = update_book
            self._save_books()
            return {"book": update_book.to_dict(), "book-id": book_id}
        else:
            raise HTTPException(404, f"Book ID {book_id} not found in database.")

    def delete_book(self, book_id: str):
        """
        Deletes a book from the bookstore.

        Args:
            book_id (str): The ID of the book to delete.

        Returns:
            dict: A dictionary containing a success message.

        Raises:
            HTTPException: If the book with the given ID is not found.
        """
        if book_id in self.books:
            del self.books[book_id]
            self._save_books()
            return {"message": "The book has been deleted"}
        else:
            raise HTTPException(404, f"Book ID {book_id} not found in database.")

    def _save_books(self):
        """
        Saves the books dictionary to the JSON file.
        """
        # with open(self.book_file, 'w') as f:
        #     json.dump([book.to_dict() for book in self.books.values()], f)

        s3 = boto3.client("s3")

        try:
            s3.put_object(
                Bucket="fast-api-storage",
                Key=self.book_file,
                Body=json.dumps([book.to_dict() for book in self.books.values()])
            )

        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print(f"Key: '{self.book_file}' does not exist!")
            else:
                print("Something else went wrong")
                raise



bookstore = BookStore(BOOKS_FILE)

@app.get('/hello-world')
async def hello_world():
    """
    Returns a simple greeting message.

    Returns:
        dict: A dictionary containing the greeting message.
    """
    return {"messages": "HELLO World!"}

@app.get("/")
def root():
    """
    Returns a welcome message to the bookstore.

    Returns:
        dict: A dictionary containing the welcome message.
    """
    return {"messages": "Welcome to the bookstore"}

@app.get("/random-book", response_model=Book)
def random_book():
    """
    Returns a random book from the bookstore.

    Returns:
        Book: A random Book object.
    """
    return random.choice(bookstore.get_all_books())

@app.get("/books", response_model=list[Book])
def list_books() -> list[Book]:
    """
    Returns a list of all books in the bookstore.

    Returns:
        list[Book]: A list of Book objects.
    """
    return bookstore.get_all_books()

# request with path params http://127.0.0.1:8000/book-by-index/<param>
# index: int -> this is a type hint
@app.get("/books-by-index/{index}")
def book_by_index(index: int = Path(ge=0, description="The index of item you would like to view")) -> Book:
    """
    Retrieves a book by its index in the bookstore.

    Args:
        index (int): The index of the book to retrieve.

    Returns:
        Book: The Book object at the specified index.
    """
    return bookstore.get_book_by_index(index)

@app.post("/add-book")
async def add_book(book: Book):
    """
    Adds a new book to the bookstore.

    Args:
        book (Book): The book object to add.

    Returns:
        dict: A dictionary containing the book's ID.
    """
    return bookstore.add_book(book)

@app.post("/update-book/{book_id}")
async def update_book(book_id: str, update_book: Book):
    """
    Updates an existing book in the bookstore.

    Args:
        book_id (str): The ID of the book to update.
        update_book (Book): The updated book object.

    Returns:
        dict: A dictionary containing the updated book and its ID.
    """
    return bookstore.update_book(book_id, update_book)

# request with query parameters http://127.0.0.1:8000/get-book?book_id=<book_id>
@app.get("/book-by-id")
def get_book(book_id: str) -> Book:
    """
    Retrieves a book by its ID.

    Args:
        book_id (str): The ID of the book to retrieve.

    Returns:
        Book: The Book object with the specified ID.
    """
    return bookstore.get_book_by_id(book_id)

@app.delete("/delete-book")
def delete_book(book_id: str):
    """
    Deletes a book from the bookstore.

    Args:
        book_id (str): The ID of the book to delete.

    Returns:
        dict: A dictionary containing a success message.
    """
    return bookstore.delete_book(book_id)