import os

from flask import Flask

from .api import books_bp, health_bp, orders_bp
from .errors import register_error_handlers
from .extensions import db, migrate


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(
        config or os.environ.get("APP_CONFIG", "book_api.config.DefaultConfig"))

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(books_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(health_bp)
    register_error_handlers(app)

    @app.cli.command("init-db")
    def init_db():
        """Tạo bảng (nếu chưa có)."""
        from . import models  # noqa: F401
        db.create_all()
        print("Database ready")

    @app.cli.command("seed")
    def seed():
        """Thêm vài cuốn sách mẫu để demo."""
        from .models import Book
        if db.session.scalar(db.select(db.func.count()).select_from(Book)):
            print("Đã có dữ liệu, bỏ qua")
            return
        db.session.add_all([
            Book(isbn="978-0132350884", title="Clean Code", author="Robert C. Martin",
                 price_cents=35000, qty_in_stock=10),
            Book(isbn="978-1449373320", title="Designing Data-Intensive Applications",
                 author="Martin Kleppmann", price_cents=45000, qty_in_stock=5),
            Book(isbn="978-0201633610", title="Design Patterns", author="Gang of Four",
                 price_cents=40000, qty_in_stock=3),
        ])
        db.session.commit()
        print("Seeded 3 books")

    return app
