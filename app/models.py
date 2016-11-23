import sqlite3 as sql
import os.path
import pandas as pd
import numpy as np
import nltk, re, pprint
import sys

ALL_JOKES = None
PRINT_VERBOSE = True

# utility print
def cprint(s):
    if PRINT_VERBOSE: print(s)

# aggregate jokes and write to combined_jokes file
def create_combined_jokes_file():
    print(os.getcwd())
    # comedy central jokes
    cc_jokes = pd.read_csv('all_cc_jokes.csv', sep = ',', index_col = 0, names = ['type', 'link', 'text'])
    cprint('Number of jokes from Comedy Central: {}'.format(cc_jokes.shape[0]))
    cprint('There are {} types of jokes on Comendy Central'.format(cc_jokes['type'].nunique()))

    # one line fun jokes
    one_liner_jokes = pd.read_csv('onelinefun.csv', encoding = "ISO-8859-1", sep = ',',
                                  index_col = 0, skiprows = 1,
                                  names = ['text', 'rating', 'num_ratings', 'tags'])
    cprint('Number of jokes from One Liner Fun: {}'.format(one_liner_jokes.shape[0]))

    # combining both jokes
    jokes_data = pd.concat([cc_jokes, one_liner_jokes], axis=0, ignore_index=True)
    cprint('Total number of jokes: {}'.format(jokes_data.shape[0]))

    jokes = jokes_data[['text', 'type', 'tags', 'rating', 'num_ratings', 'link']]
    jokes.to_csv('combined_jokes.csv', index_label='ID')

    return True

# load jokes and return all jokes in the data frame
def load_jokes():
    global ALL_JOKES
    if ALL_JOKES is None:
        if not os.path.isfile('combined_jokes.csv'):
            create_combined_jokes_file()
        ALL_JOKES = pd.read_csv('combined_jokes.csv', sep = ',', index_col = 0)
    return ALL_JOKES

# get n random jokes
def get_random_jokes(n = 20, random_state = None):
    global ALL_JOKES
    if ALL_JOKES is None:
        load_jokes()
    jokes_df = ALL_JOKES.sample(n=n, replace=False, random_state=random_state)
    return jokes_df
