#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, MetaData, ForeignKey, Sequence
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    uid = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    text = Column(String(255), nullable=False)

    def __init__(self, date, text):
        self.date = date
        self.text = text

    def __repr__(self):
        return "<Message(%s - %s - %s)>" % (self.uid, self.date, self.text)

class Version(Base):
    __tablename__ = 'versions'
    version = Column(String(100), primary_key=True)
    date = Column(DateTime, nullable=False)

    def __init__(self, version, date):
        self.version = version
        self.date = date

    def __repr__(self):
        return "<Version(%s - %s)>" % (self.uid, self.date)

def create_tables(engine):
    Base.metadata.create_all(engine)