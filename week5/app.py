from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (CheckConstraint, DateTime, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import mapped_column, relationship

db = SQLAlchemy()