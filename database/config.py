import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()


db_user = os.environ.get('POSTGRES_USER')
db_key = os.environ.get('POSTGRES_PASSWORD')
db_port = os.environ.get('DATABASE_PORT')
db_url = os.environ.get('POSTGRES_HOST')
db_database = os.environ.get('POSTGRES_DATABASE')


SQLALCHEMY_DATABASE_URL = 'postgresql://' + db_user + \
    ':' + db_key + '@' + db_url + ':' + db_port + '/' + db_database


engine = create_engine(SQLALCHEMY_DATABASE_URL, )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
