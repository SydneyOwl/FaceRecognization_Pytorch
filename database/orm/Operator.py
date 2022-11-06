from sqlalchemy import VARCHAR, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(10), unique=True)
    password = Column(VARCHAR(100), unique=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password