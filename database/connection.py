from os import getenv
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


load_dotenv()

DATABASE_URI = f"mysql+pymysql://{getenv('MYSQL_USER')}:{getenv('MYSQL_PASSWORD')}@{getenv('MYSQL_HOST')}:{getenv('MYSQL_PORT')}/{getenv('MYSQL_DB')}?charset=utf8"

Base = declarative_base()


class Database():
    def __init__(self) -> None:
        self.connection_is_active = False
        self.engine = None

    def get_db_connection(self):
        if self.connection_is_active == False:
            try:
                self.engine = create_engine(DATABASE_URI)
                self.connection_is_active = True
                return self.engine
            except Exception as ex:
                print("Error connecting to DB : ", ex)
        return self.engine

    def get_db_session(self):
        try:
            engine = self.get_db_connection()
            Session = sessionmaker(bind=engine)
            session = Session()
            return session
        except Exception as ex:
            print("Error getting DB session : ", ex)
            return None
