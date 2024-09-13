import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()


db_user = os.environ.get('DATABASE_USER')
db_key = os.environ.get('DATABASE_KEY')
db_port = os.environ.get('DATABASE_PORT')
db_url = os.environ.get('DATABASE_URL')


SQLALCHEMY_DATABASE_URL = 'postgresql://' + db_user + \
    ':' + db_key + '@' + db_url + ':' + db_port + '/postgres'


engine = create_engine(SQLALCHEMY_DATABASE_URL, )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
