# Module-level proxy: chưa gắn app, factory sẽ gọi init_app().
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
