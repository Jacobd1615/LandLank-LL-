from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Date, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


# Define models 
