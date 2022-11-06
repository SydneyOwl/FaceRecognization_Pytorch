from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import config
Base = declarative_base()

engine = create_engine("mysql://{}:{}@{}:{}/{}?charset=utf8".format(config.mysql_cfg['username'], config.mysql_cfg['password'], config.mysql_cfg['host'], config.mysql_cfg['port'], config.mysql_cfg['db']), echo=True,
                       pool_size=8,
                       pool_recycle=3600)
Base.metadata.create_all(engine)
DbSession = sessionmaker(bind=engine)
session = DbSession()