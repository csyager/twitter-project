import twitter
import os
from dotenv import load_dotenv
import psycopg2
import logging
import threading
import time
import requests
load_dotenv()

# get key environment variables
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN_KEY = os.getenv("ACCESS_TOKEN_KEY")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# connect to twitter api using keys from environment vars
api = twitter.Api(consumer_key=CONSUMER_KEY,
                    consumer_secret=CONSUMER_SECRET,
                    access_token_key=ACCESS_TOKEN_KEY,
                    access_token_secret=ACCESS_TOKEN_SECRET,
                    sleep_on_rate_limit=True)

# connect to local postgresql database
conn = psycopg2.connect(host="localhost", database="twitter", user="postgres", password="postgres")
cur = conn.cursor()

# config logging
logging.basicConfig(filename="app.log", filemode="w", format="[%(asctime)s]: %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)