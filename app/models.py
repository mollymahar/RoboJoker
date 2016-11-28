import sqlite3 as sql
import os.path
import pandas as pd
import numpy as np
import nltk, re, pprint
import sys
from sklearn import linear_model
import random
import json

ALL_JOKES = None
PRINT_VERBOSE = True
ALL_LATENT_TOPICS = None

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

def load_latent_topics():
    global ALL_LATENT_TOPICS
    if ALL_LATENT_TOPICS is None:
        try:
            ALL_LATENT_TOPICS = np.load('latent_topics.npy')
            print('successfully loaded latent topics for jokes from file')
            return ALL_LATENT_TOPICS
        except:
            print('latent topics file cannot be loaded')
            return None
    return ALL_LATENT_TOPICS

# get n random jokes
def get_random_jokes(n = 20, random_state = None):
    global ALL_JOKES
    if ALL_JOKES is None:
        load_jokes()
    jokes_df = ALL_JOKES.sample(n=n, replace=False, random_state=random_state)
    return jokes_df

# return rating guestimate given existing ratings
def guess_ratings(indices, ratings, joke_features):
    clf = linear_model.Ridge (alpha = .1)
    y_pred = clf.fit(joke_features[indices], ratings).predict(joke_features)
    y_pred -= np.mean(y_pred)
    y_pred *= 1.5/np.std(y_pred)
    y_pred += 2.5
    y_pred = y_pred.round()
    y_pred[np.where(y_pred > 5)] = 5
    y_pred[np.where(y_pred < 1)] = 1
    return y_pred

def write_response_to_json(filename, ratings_dict):
    with open(filename, 'w') as outfile:
        json.dump(ratings_dict, outfile, separators=(',', ':'))

# get top five jokes
def get_top_five_jokes(ratings_dict):
    all_jokes = load_jokes()['text']
    all_latent_topics = load_latent_topics()
    if all_latent_topics is None:
        return None, None, None

    rating_tuples = list(ratings_dict.items())
    indices = []
    ratings = []
    for rating in rating_tuples:
        if rating[1] == 'None':
            pass
        else:
            indices += [int(rating[0])]
            ratings += [int(rating[1])]

    indices, ratings = np.asarray(indices), np.asarray(ratings)
    guesses = guess_ratings(indices, ratings, all_latent_topics)

    top_five_idx, top_five_txt, top_five_rating = [], [], []

    joke_rankings = np.argsort(guesses)

    while len(top_five_idx) < 5:
        pos = random.randint(-500, -1)
        joke_index = joke_rankings[pos]

        while joke_index in indices or joke_index in top_five_idx:
            pos -= 1
            joke_index = joke_rankings[pos]

        top_five_idx += [joke_index]
        top_five_txt += [all_jokes[joke_index]]
        top_five_rating += [guesses[joke_index]]

    # print(top_five_idx)
    # print(top_five_txt)
    # print(top_five_rating)
    return top_five_idx, top_five_txt, top_five_rating
