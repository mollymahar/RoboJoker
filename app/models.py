import sqlite3 as sql
import os.path
import pandas as pd
import numpy as np
import nltk, re, pprint
import sys
from sklearn import linear_model
import random
import json
import gensim
import gensim.models.doc2vec
from gensim.models import Doc2Vec



ALL_JOKES = None
PRINT_VERBOSE = True
ALL_LATENT_TOPICS = None
jokes_text_filename = 'nodups_combined_jokes.csv'
features_filename = 'combined_features_unique.npy'
model = Doc2Vec.load('doc2vecmodel.pkl')


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
    NUM_JOKES = jokes_data.shape[0]

    jokes = jokes_data[['text', 'type', 'tags', 'rating', 'num_ratings', 'link']]
    unique_jokes = raw_jokes.drop_duplicates(subset=['text'])
    unique_jokes.reset_index(inplace = True)
    unique_jokes.to_csv(jokes_text_filename, index_label='ID')

    return True

# load jokes and return all jokes in the data frame
def load_jokes():
    global ALL_JOKES
    if ALL_JOKES is None:
        if not os.path.isfile(jokes_text_filename):
            create_combined_jokes_file()
        ALL_JOKES = pd.read_csv(jokes_text_filename, encoding = "ISO-8859-1", sep = ',', index_col = 0)
    return ALL_JOKES

def load_latent_topics():
    global ALL_LATENT_TOPICS
    if ALL_LATENT_TOPICS is None:
        try:
            ALL_LATENT_TOPICS = np.load(features_filename)
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
    y_pred *= 1.0/np.std(y_pred)
    y_pred += 2.5
    return y_pred

def write_response_to_json(filename, ratings_dict):
    with open(filename, 'w') as outfile:
        json.dump(ratings_dict, outfile, separators=(',', ':'))

# get top five jokes
# def get_top_five_jokes(ratings_dict):
#     all_jokes = load_jokes()['text']
#     all_latent_topics = load_latent_topics()
#     if all_latent_topics is None:
#         return None, None, None
#
#     rating_tuples = list(ratings_dict.items())
#     indices = []
#     ratings = []
#     for rating in rating_tuples:
#         if rating[1] == 'None':
#             pass
#         else:
#             indices += [int(rating[0])]
#             ratings += [int(rating[1])]
#
#     indices, ratings = np.asarray(indices), np.asarray(ratings)
#     guesses = guess_ratings(indices, ratings, all_latent_topics)
#
#     top_five_idx, top_five_txt, top_five_rating = [], [], []
#
#     joke_rankings = np.argsort(guesses)
#
#     while len(top_five_idx) < 5:
#         pos = random.randint(-200, -1)
#         joke_index = joke_rankings[pos]
#
#         if joke_index not in indices and joke_index not in top_five_idx:
#             joke_index = joke_rankings[pos]
#             top_five_idx += [joke_index]
#             top_five_txt += [all_jokes[joke_index]]
#             top_five_rating += [guesses[joke_index]]
#
#     return top_five_idx, top_five_txt, top_five_rating

# get top five jokes
def get_n_jokes(ratings_dict, n, min_index, max_index):
    all_jokes = load_jokes()['text']
    all_latent_topics = load_latent_topics()

    # if loading latent topics is unsuccessful, return None
    if all_latent_topics is None:
        return None, None, None

    # dynamically increase the search range if we are running out of jokes
    # if we exhausts all jokes, return None, None, None
    num_seen = len(ratings_dict)
    seen_jokes = set(int(i) for i in ratings_dict.keys())

    while (max_index - min_index) < n + num_seen:
        if np.sign(min_index) == 1:
            max_index = max_index*2
            if abs(min_index) > len(all_jokes):
                return None, None, None
        else:
            min_index = min_index*2
            if max_index >= len(all_jokes):
                return None, None, None

    rating_tuples = list(ratings_dict.items())
    indices, ratings = [], []
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

    while len(top_five_idx) < n:
        pos = random.randint(min_index, max_index)
        # print(pos)
        joke_index = joke_rankings[pos]

        if joke_index not in seen_jokes and joke_index not in top_five_idx:
            joke_index = joke_rankings[pos]
            top_five_idx += [joke_index]
            top_five_txt += [all_jokes[joke_index]]
            top_five_rating += [guesses[joke_index]]

    return top_five_idx, top_five_txt, top_five_rating

def get_jokes(indices):
    all_jokes = load_jokes()['text']
    jokes_text = [all_jokes[int(i)] for i in indices]
    return jokes_text

def get_good_jokes(ratings_dict):
    return get_n_jokes(ratings_dict, 5, -201, -1)

def get_bad_jokes(ratings_dict):
    return get_n_jokes(ratings_dict, 5, 0, 200)

def get_median_jokes(ratings_dict):
    global ALL_JOKES
    return get_n_jokes(ratings_dict, 5, ALL_JOKES.shape[0]//2-100, ALL_JOKES.shape[0]//2+100)

# Convert text to lower-case and strip punctuation/symbols from words
def normalize_text(text):
    norm_text = text.lower()

    # Replace breaks with spaces
    norm_text = norm_text.replace('<br />', ' ')

    # Pad punctuation with spaces on both sides
    for char in ['.', '"', ',', '(', ')', '!', '?', ';', ':']:
        norm_text = norm_text.replace(char, ' ' + char + ' ')

    return norm_text

def indices_of_similar(joke):
    global model
    # joke = ("Yo mama's like a brick. dirty, flat on both sides, and always getting laid by Mexicans.")
    tokens = gensim.utils.to_unicode(normalize_text(joke)).split()
    vector = model.infer_vector(tokens)
    # print(dir(model))
    sims = model.docvecs.most_similar([vector], topn=model.docvecs.count)  # get *all* similar documents
    # just take first element from generated pairs of indexes and scores
    sims = list(map(lambda x: int(x[0]), sims))
    # print(sims[:5])
    # print(get_jokes(sims[:4]))
    return sims[:4]
    # print(u'TARGET: «%s»\n' % (sample_text))
    # print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
    # for label, index in [('MOST', 2), ('MEDIAN', len(sims)//2), ('LEAST', len(sims) - 1)]:
        # print(u'%s %s: «%s»\n' % (label, sims[index], ' '.join(alldocs[sims[index][0]].words)))

