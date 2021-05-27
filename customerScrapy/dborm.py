from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def getsession():
    '''
    获取Orm信息
    :return:
    '''
    settings = get_project_settings()
    host = settings.get('MYSQL_HOST')
    user = settings.get('MYSQL_USER')
    password = settings.get('MYSQL_PASSWD')
    db = settings.get('MYSQL_DBNAME')
    config = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8&use_unicode=1' % (user, password, host, db)
    engine = create_engine(config, encoding="utf-8", echo=False)
    session = sessionmaker(bind=engine)
    DBSession = session()
    return DBSession
