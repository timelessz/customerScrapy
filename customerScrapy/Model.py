# coding: utf-8
from sqlalchemy import Column, String, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Category(Base):
    __tablename__ = 'category'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(20), server_default=text("''"))
    en_name = Column(String(20))
    link = Column(String(100))
    type_id = Column(INTEGER(11), server_default=text("'0'"))
    created_at = Column(INTEGER(11))
    updated_at = Column(INTEGER(11))


class Industry(Base):
    __tablename__ = 'industry'

    id = Column(INTEGER(11), primary_key=True)
    cat_id = Column(INTEGER(11))
    name = Column(String(20), server_default=text("''"))
    en_name = Column(String(20))
    link = Column(String(200))
    cus_list_link = Column(String(200))
    all_page_num = Column(INTEGER(11))
    current_page_num = Column(INTEGER(11))
    created_at = Column(INTEGER(11))
    updated_at = Column(INTEGER(11))


class Type(Base):
    __tablename__ = 'type'

    id = Column(INTEGER(10), primary_key=True)
    name = Column(String(50))
    en_name = Column(String(50))
    created_at = Column(INTEGER(11))
    updated_at = Column(INTEGER(11))


class Customer(Base):
    __tablename__ = 'customer'

    id = Column(INTEGER(11), primary_key=True)
    industry_id = Column(INTEGER(11))
    name = Column(String(100), server_default=text("''"))
    en_name = Column(String(200), server_default=text("''"))
    address = Column(String(200), server_default=text("''"))
    city = Column(String(20))
    province = Column(String(20))
    contact = Column(String(50), server_default=text("''"))
    dept = Column(String(50), server_default=text("''"))
    position = Column(String(50), server_default=text("''"))
    telephone = Column(String(50))
    mobile = Column(String(50), server_default=text("''"))
    fax = Column(String(50), server_default=text("''"))
    showroom = Column(String(200), server_default=text("''"))
    website = Column(String(200), server_default=text("''"))
    type = Column(String(10), server_default=text("''"))
    created_at = Column(INTEGER(11))
    updated_at = Column(INTEGER(11))
