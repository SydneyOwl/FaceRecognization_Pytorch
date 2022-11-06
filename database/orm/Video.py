from sqlalchemy import DATETIME, VARCHAR, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(VARCHAR(100), primary_key=True)
    original_name = Column(VARCHAR(10), unique=True)
    dir = Column(VARCHAR(100), unique=False)
    processed = Column(Integer, unique=False)
    opid = Column(Integer, unique=False)
    thumb = Column(VARCHAR(100), unique=False)
    time = Column(DATETIME, unique=False)
    # time = 
    def __init__(self, uuid,opid,original_name, dir,processed,thumb,time):
        self.id=uuid
        self.processed = processed
        self.dir = dir
        self.original_name = original_name
        self.opid=opid
        self.thumb = thumb
        self.time=time