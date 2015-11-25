# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base
from settings import PUBLIC_STRING, ECHOSQL


Base = declarative_base()


def get_engine():
    engine = create_engine(
        PUBLIC_STRING,
        convert_unicode=True,
        echo=ECHOSQL,
        pool_recycle=3600
    )
    return engine


def get_db():
    Session = sessionmaker()
    Session.configure(autoflush=True, bind=get_engine())
    return scoped_session(Session)
