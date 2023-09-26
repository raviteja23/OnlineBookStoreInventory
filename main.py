from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI()

# Define the SQLAlchemy engine and session
SQLALCHEMY_DATABASE_URL = "sqlite:///./bookstore.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the SQLAlchemy Base
Base = declarative_base()

# Define the Book model
class Book(BaseModel):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    def update_quantity(self, new_quantity: int):
        self.quantity = new_quantity

# Define the Bookstore class
class Bookstore:
    def __init__(self, session):
        self.session = session

    def add_book(self, book: Book):
        self.session.add(book)
        self.session.commit()
    
    def remove_book(self, book_id: str):
        book = self.session.query(Book).filter_by(book_id=book_id).first()
        if book:
            self.session.delete(book)
            self.session.commit()
            return True
        return False
    
    def update_book(self, book_id: str, title: Optional[str] = None, author: Optional[str] = None, 
                    price: Optional[float] = None, quantity: Optional[int] = None):
        book = self.session.query(Book).filter_by(book_id=book_id).first()
        if book:
            if title is not None:
                book.title = title
            if author is not None:
                book.author = author
            if price is not None:
                book.price = price
            if quantity is not None:
                book.quantity = quantity
            self.session.commit()
            return True
        return False
    
    def get_book(self, book_id: str):
        return self.session.query(Book).filter_by(book_id=book_id).first()
    
    def get_all_books(self):
        return self.session.query(Book).all()
    
    def search_book(self, book_id: str):
        return self.session.query(Book).filter_by(book_id=book_id).first()

# Define the Order model
class Order(BaseModel):
    book_id: str
    quantity: int
    
    def get_total_price(self, bookstore: Bookstore):
        book = bookstore.get_book(self.book_id)
        if book is None:
            return None
        return book.price * self.quantity
    
    
class BookOut(BaseModel):
    id: int
    title: str
    author: str
    price: float
    stock: int



class BooksOut(BaseModel):
    books: List[BookOut]

class ErrorResponse(BaseModel):
    detail: str

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the bookstore instance with the database session
bookstore = Bookstore(SessionLocal())

# Define the FastAPI routes
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/books/")
def add_book(book: Book, db: Session = Depends(get_db)):
    bookstore.add_book(book)
    
@app.get("/books/", response_model=BooksOut, response_model_exclude_unset=True)
async def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = crud.get_books(db, skip=skip, limit=limit)
    return {"books": books}
