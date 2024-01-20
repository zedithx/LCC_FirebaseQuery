import os
import logging
from datetime import datetime

import firebase_admin
import random

from dotenv import load_dotenv
from firebase_admin import db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
load_dotenv()

"""Initialising firebase creds"""
cred_obj = firebase_admin.credentials.Certificate('./creds.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': os.environ.get("DATABASE_URL")
})
ref = db.reference("/")

"""Initialising variables"""
name_list = []
poster_dict = {}
telegram_id_list = []
NUMBER_OF_WINNERS = 5


# Get all participants first names
def traverse_and_get_keys(inp):
    if isinstance(inp.get(), dict):
        # If the current node is a dictionary, recursively traverse and get keys
        for key in inp.get().keys():
            traverse_and_get_keys(inp.child(key))
    else:
        # If the current node is a leaf node, print the full path and key
        name_list.append(inp.key)


# Return the base node and count for each base node
# Count for urop and fifth row
def count_poster(inp):
    if inp == 'OVERSEAS':
        if ref.child(inp).get():
            for country in ref.child(inp).get().keys():  # country ref
                for poster in ref.child(inp).child(country).get().keys():  # poster ref
                    poster_dict[poster] = len(ref.child(inp).child(country).child(poster).get())
    else:
        if ref.child(inp).get():
            for poster in ref.child(inp).get().keys():
                poster_dict[poster] = len(ref.child(inp).child(poster).get())


def tabulate_poster_max(size: int):
    sorted_poster_dict = list(sorted(poster_dict.items(), key=lambda x: x[1], reverse=True))
    return [poster for poster in sorted_poster_dict[0:size]]


def get_telegram_ids(inp, telegram_id_list):
    if inp == 'OVERSEAS':
        if ref.child(inp).get():
            for country in ref.child(inp).get().keys():  # country ref
                for poster in ref.child(inp).child(country).get().keys():  # poster ref
                    telegram_id_list += list(ref.child(inp).child(country).child(poster).get().keys())
    else:
        if ref.child(inp).get():
            for poster in ref.child(inp).get().keys():
                telegram_id_list += list(ref.child(inp).child(poster).get().keys())


# Choosing Lucky Draw Winner
start_time = datetime.now()
traverse_and_get_keys(ref)
print(f"Time elapsed for Lucky Draw:{datetime.now() - start_time}")
print(f'Lucky Draw winners: {random.sample(name_list, k=3)}\n')

# Find most popular poster
start_time = datetime.now()
count_poster("FIFTHROW")
count_poster("OVERSEAS")
count_poster("UROP")
print(f"Time elapsed for Popular Poster:{datetime.now() - start_time}")
print(f'Most Popular Posters: {tabulate_poster_max(3)}\n')

# get list of telegram_ids
start_time = datetime.now()
get_telegram_ids("FIFTHROW", telegram_id_list)
get_telegram_ids("OVERSEAS", telegram_id_list)
get_telegram_ids("UROP", telegram_id_list)
print(f"Time elapsed for Popular Poster:{datetime.now() - start_time}")
print(f"Telegram IDs: {set(telegram_id_list)}")
