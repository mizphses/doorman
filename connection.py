"""This module contains the connection to the database"""
import os

from os.path import join, dirname
from urllib.parse import urlparse
from psycopg2 import connect
from dotenv import load_dotenv

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

url = urlparse(os.environ.get("DB_URL"))

def get_connection():
    """
    This function makes a connection to the database
    """
    dsn = f"dbname={url.path[1:]} user={url.username} password={url.password}\
        host={url.hostname} port={url.port}"
    return connect(dsn)
