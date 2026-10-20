from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (CheckConstraint, DateTime, ForeignKey, Integer, String, Text)
from sqlalchemy.orm import mapped_column, relationship

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = "categories"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    slug = mapped_column(String(100), unique=True, nullable=False)

    books = relationship("Book", back_populates="category")  

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}

class BookAuthor(db.Model):
    __tablename__ = "book_authors"

    book_id = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    author_id = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True)

    book = relationship("Book", back_populates="authors_links")
    author = relationship("Author", back_populates="books_links")

    def to_dict(self):
        return {"book_id": self.book_id, "author_id": self.author_id}

class Book(db.Model):
    __tablename__ = "books"

    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(200), nullable=False)
    description = mapped_column(Text, nullable=False)
    stock = mapped_column(Integer, nullable=False, default=0)
    category_id = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    published_date = mapped_column(DateTime(timezone=True), nullable=True)

    category = relationship("Category", back_populates="books")
    authors_links = relationship("BookAuthor", back_populates="book",
                                    cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="book",
                                    cascade="all, delete-orphan")

    @classmethod
    def from_payload(cls, payload):
        book = cls(
            title=payload.get("title"),
            description=payload.get("description"),
            category_id=payload.get("category_id"),
            stock=payload.get("stock", 0),
            published_date=payload.get("published_date")
        )
        for author in payload.get("authors", []):
            book.authors_links.append(BookAuthor(author_id=author["id"]))
        return book

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "stock": self.stock,
            "category_id": self.category_id,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "authors": [link.author.to_dict() for link in self.authors_links],
        }

class Author(db.Model):
    __tablename__ = "authors"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)

    books_links = relationship("BookAuthor", back_populates="author",
                                    cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "name": self.name}

class User(db.Model):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String(50), unique=True, nullable=False)
    email = mapped_column(String(100), unique=True, nullable=False)

    reviews = relationship("Review", back_populates="user")

    def to_dict(self):
        return {"id": self.id, "username": self.username}

class Review(db.Model):
    __tablename__ = "reviews"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range"),)

    review_id = mapped_column(Integer, primary_key=True)
    rating = mapped_column(Integer, nullable=False)
    book_id = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    user_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def to_dict(self):
        return {
            "review_id": self.review_id,
            "rating": self.rating,
            "book_id": f"book_{self.book_id}",
            "user_id": f"user_{self.user_id}",
        }
    
