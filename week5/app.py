import os
from datetime import datetime

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from models import Author, Book, BookAuthor, Category, db
from routes.books import bp as books_bp


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///bookstore.db"),
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),  # dùng để ký cursor
    )
    app.json.sort_keys = False
    app.json.ensure_ascii = False
    if config:
        app.config.update(config)

    db.init_app(app)
    app.register_blueprint(books_bp)

    @app.errorhandler(HTTPException)
    def _http_error(e):
        return jsonify(error=e.name.lower().replace(" ", "_"), message=e.description), e.code

    @app.cli.command("seed")
    def seed():
        """flask --app app seed : xoá DB, tạo lại và thêm 45 sách mẫu."""
        db.drop_all()
        db.create_all()
        seed_data()
        print("Seeded 45 books.")

    with app.app_context():
        db.create_all()
    return app


def seed_data(n_books=45):
    """Dữ liệu cố ý có giá trị trùng (stock, title) và published_date NULL
    để kiểm tra tie-break của cursor."""
    cats = [Category(name="Công nghệ", slug="tech"),
            Category(name="Tiểu thuyết", slug="novel"),
            Category(name="Kinh tế", slug="business")]
    authors = [Author(name=f"Author {i}") for i in range(1, 6)]
    db.session.add_all(cats + authors)
    db.session.flush()

    for i in range(1, n_books + 1):
        book = Book(
            title=f"Book {i % 7:02d}",                     # 7 tiêu đề lặp lại
            description=f"Mô tả sách số {i}",
            stock=i % 4,                                    # chỉ 4 giá trị stock
            category_id=cats[i % 3].id,
            published_date=None if i % 5 == 0 else datetime(2000 + i % 9, 1 + i % 12, 1),
        )
        book.authors_links.append(BookAuthor(author_id=authors[i % 5].id))
        db.session.add(book)
    db.session.commit()


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
