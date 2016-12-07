from app import myapp, models
from flask import render_template, redirect, request, session, url_for, escape, flash
from .forms import QuestionForm, EvaluateForm
import requests, json, re, datetime
from time import time
import numpy as np
from .tools import s3_upload
import random

"""
View functions:
* Handle logic on the front-end
* Access the models file to use SQL functions
"""

RANDOM_ANIMAL_PAGE = False

# landing redirect
@myapp.route('/')
@myapp.route('/index')
def index():
    # session.pop('page', None)
    # we don't pop the baseline_result anymore since we need to use it for both evaluation and get good jokes
    # session.pop('baseline_result', None)

    next_page = 'page_1' if RANDOM_ANIMAL_PAGE else 'evaluate'

    rated_baseline = 'False' if 'baseline_result' not in session else 'True'
    return render_template('index.html', rated_baseline = rated_baseline, next_page = next_page)

# display some random jokes
@myapp.route('/baseline', methods=['GET','POST'])
def baseline():

    jokes_df = models.get_random_jokes(20, random_state=88)
    jokes_idx = list(jokes_df.index)
    jokes_text = list(jokes_df['text'])

    # page: the current page/stage for the baseline, can be [1,2,3,4]
    page = 1 if 'page' not in session else int(session['page'])
    offset = (page - 1)*5

    form = QuestionForm()
    error = None

    if form.validate_on_submit():
        # get user ratings from form data
        ratings = [field.data for field in form]
        # first field is CSRF field - remove that from the output
        ratings = ratings[1:]

        if all(rating == 'None' for rating in ratings):
            error = 'Please rate at least 1 joke before proceeding!'
            return render_template('baseline.html',
            jokes = jokes_text[offset:offset + 5], offset = offset, form = form, error = error)

        # result: a dictionary of joke ID: user rating so far
        # current result is stored as a variable in session
        result = dict() if 'baseline_result' not in session else json.loads(session['baseline_result'])
        for i in range(len(ratings)):
            if ratings[i] != 'None':
                result[str(jokes_idx[offset + i])] = ratings[i]

        session['baseline_result'] = json.dumps(result)

        # if reached last page, move onto next phase
        # otherwise increment page by 1
        if page == 4:
            # writing user's response into json file
            if 'filename' not in session:
                session['filename'] = 'responses/' + str(round(time())) + '.json'
            filename = session['filename']
            models.write_response_to_json(filename, result)
            return redirect('/update')
        else:
            session['page'] = str(page + 1)
            return redirect('/baseline')

    return render_template('baseline.html',
    jokes = jokes_text[offset:offset + 5], offset = offset, form = form, error = error)

@myapp.route('/update', methods=['GET','POST'])
def update():
    session['result'] = session['baseline_result']
    global RANDOM_ANIMAL_PAGE
    if RANDOM_ANIMAL_PAGE:
        page_orders = ['bee', 'fish', 'octopus']
        random.shuffle(page_orders)

        session['page_1'] = page_orders[0]
        session['page_2'] = page_orders[1]
        session['page_3'] = page_orders[2]

        next_page = 'page_1'

    else:
        session['reload'] = 'true'
        next_page = 'evaluate'

    return render_template('update.html', next_page = next_page)

###########################################################

"""
Option 1
Good/random/bad joke randomization with animal pages
"""
@myapp.route('/page_1', methods=['GET', 'POST'])
def page_1():
    joke_getter = get_joke_getter(session['page_1'])
    current_html_page = session['page_1'] + '.html'
    next_html_handler = '/page_2'
    return recommended_jokes(joke_getter, current_html_page, next_html_handler)

@myapp.route('/page_2', methods=['GET', 'POST'])
def page_2():
    joke_getter = get_joke_getter(session['page_2'])
    current_html_page = session['page_2'] + '.html'
    next_html_handler = '/page_3'
    return recommended_jokes(joke_getter, current_html_page, next_html_handler)

@myapp.route('/page_3', methods=['GET', 'POST'])
def page_3():
    joke_getter = get_joke_getter(session['page_3'])
    current_html_page = session['page_3'] + '.html'
    next_html_handler = '/completion'
    return recommended_jokes(joke_getter, current_html_page, next_html_handler)

# HELPER FUNCTIONS
def get_joke_getter(page_type):
    joke_getter = None
    if page_type == 'bee':
        joke_getter = models.get_good_jokes
    elif page_type == 'fish':
        joke_getter = models.get_median_jokes
    else:
        joke_getter = models.get_bad_jokes
    return joke_getter

def recommended_jokes(joke_getter, current_html_page, next_html_handler):
    result = json.loads(session['result'])
    error = None

    jokes_idx, jokes_text, guessed_ratings = joke_getter(result)

    if jokes_idx is None:
        error = 'This is embarrassing - we are having some backend issues at the moment, please check back later'

    form = QuestionForm()

    if form.validate_on_submit():
        # get user ratings from form data
        ratings = [field.data for field in form]
        # first field is CSRF field - remove that from the output
        ratings = ratings[1:]

        if all(rating == 'None' for rating in ratings):
            error = 'Please rate at least 1 joke before proceeding!'
            return render_template(current_html_page,
            error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)

        # result: a dictionary of joke ID: user rating so far
        for i in range(len(ratings)):
            if ratings[i] != 'None':
                result[str(jokes_idx[i])] = ratings[i]

        session['result'] = json.dumps(result)

        # writing user's response into json file
        filename = session['filename']
        models.write_response_to_json(filename, result)

        return redirect(next_html_handler)

    return render_template(current_html_page,
    error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)

###########################################################

"""
Option 2
Evaluate 15 random jokes (5 good, 5 random, 5 bad) and give overall ratings
"""
# an infinite loop that shows user 15 random jokes
@myapp.route('/evaluate', methods=['GET','POST'])
def evaluate():
    result = json.loads(session['result'])
    error = None

    # ====================
    # get 15 random jokes - 5 good, 5 random(medium), and 5 bad ones
    # shuffle them in random order, variable evaluate_key keeps track of
    # which jokes are which
    # ====================
    if session['reload'] == 'true':
        models_list = [models.get_good_jokes(result), models.get_median_jokes(result), models.get_bad_jokes(result)]
        jokes_idx, guessed_ratings = [], []
        for model in models_list:
            jokes_idx += model[0]
            guessed_ratings += model[2]

        # shuffle the list of jokes
        shuffling_orders = np.arange(15)
        np.random.shuffle(shuffling_orders)

        # evaluate_key tells you which jokes are good(1), bad(-1),
        # or random(0) in the newly shuffled list
        evaluate_key = (shuffling_orders < 5).astype(int) + -1*(shuffling_orders > 9).astype(int)
        jokes_idx, guessed_ratings = shuffle_jokes(shuffling_orders, jokes_idx, guessed_ratings)

        session['reload'] = 'false'
        session['currentjokes'] = json.dumps({
        'jokes_idx':jokes_idx,
        'guessed_ratings':guessed_ratings,
        'evaluate_key':np.array(evaluate_key).tolist()})

        if len(jokes_idx) == 0:
            error = 'This is embarrassing - we are having some backend issues at the moment, please check back later'
    else:
        current_jokes = json.loads(session['currentjokes'])
        jokes_idx = current_jokes['jokes_idx']
        guessed_ratings = current_jokes['guessed_ratings']
        evaluate_key = current_jokes['evaluate_key']

    # get jokes text based on indices
    # dynamically loading jokes to avoid overflow issue with caching them
    jokes_text = models.get_jokes(jokes_idx)

    # ====================
    # get user evaluation input
    # ====================
    form = EvaluateForm()
    if form.validate_on_submit():
        # get user ratings from form data
        ratings = [field.data for field in form]
        # first field is CSRF field - remove that from the output
        ratings = ratings[1:]

        if all(rating == 'None' for rating in ratings):
            error = 'Please rate at least 1 joke before proceeding!'
            return render_template('recommendation.html',
            error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)

        # result: a dictionary of joke ID: user rating so far
        # if 'evaluateresults' in session:
        #      evaluate_results = json.loads(session['evaluateresults'])
        #      p_jokes_idx, p_guessed_ratings, p_ratings, p_evaluate_key = get_past_eval_results(evaluate_results)
        # else:
        evaluate_results = dict()
        p_jokes_idx, p_guessed_ratings, p_ratings, p_evaluate_key = [], [], [], []

        for i in range(len(ratings)):
            if ratings[i] != 'None':
                result[str(jokes_idx[i])] = ratings[i]
                p_jokes_idx.append(jokes_idx[i])
                p_guessed_ratings.append(guessed_ratings[i])
                p_ratings.append(ratings[i])
                p_evaluate_key.append(evaluate_key[i])

        # update session variable to store the latest user input
        session['result'] = json.dumps(result)
        session['evaluateresults'] = json.dumps({
        'jokes_idx':p_jokes_idx,
        'guessed_ratings':p_guessed_ratings,
        'ratings':p_ratings,
        'evaluate_key':np.array(p_evaluate_key).tolist()})

        # writing user's response into json file
        filename = session['filename']
        models.write_response_to_json(filename, result)

        # if request.form['submit'] == 'Gimme More':
        #     session['reload'] = 'true'
        #     return redirect('/evaluate')
        # elif request.form['submit'] == 'I\'m Done':
        return redirect('evaluateresults')

    return render_template('recommendation.html',
    error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)

# show evaluation result
@myapp.route('/evaluateresults', methods=['GET','POST'])
def evaluateresult():
    evaluate_results = json.loads(session['evaluateresults'])
    error = None

    jokes_idx, guessed_ratings, ratings, evaluate_key = get_past_eval_results(evaluate_results)

    if len(jokes_idx) == 0:
        error = 'This is embarrassing - we are having some backend issues at the moment, please check back later'

    # get the average user rating for each type of jokes
    avgs = avg_ratings_by_labels(ratings, evaluate_key)
    good_avg, median_avg, bad_avg = avgs[1], avgs[0], avgs[-1]

    # convert numeric labels to strings
    eval_mapping = ['median', 'good', 'bad']
    groups = [eval_mapping[l] for l in evaluate_key]

    # round raw guessed ratings for display
    rounded_ratings = list(map(round_cap_rating, guessed_ratings))

    # get jokes text for display
    jokes_text = models.get_jokes(jokes_idx)

    user_submission = {
    'total_rated':len(ratings),
    'avgs':avgs,
    'jokes index': jokes_idx,
    'jokes text': jokes_text,
    'guessed ratings': guessed_ratings,
    'actual ratings': ratings,
    'baseline_result': json.loads(session['baseline_result'])
    }

    # saving it to amazon s3
    s3_upload(json.dumps(user_submission))

    filename = session['filename']
    models.write_response_to_json(filename, json.dumps(user_submission))

    return render_template('evaluateresults.html',
    error = error, jokes = jokes_text, ratings = ratings,
    group = groups, guessed_ratings = rounded_ratings,
    good_avg = good_avg, bad_avg = bad_avg, median_avg = median_avg)

# HELPER FUNCTIONS
# return shuffled jokes given the shuffling order
def shuffle_jokes(shuffling_orders, indices, ratings):
    shuffled_indices, shuffled_ratings = [], []
    for index in shuffling_orders:
        shuffled_indices.append(int(indices[index]))
        shuffled_ratings.append(ratings[index])
    return shuffled_indices, shuffled_ratings

# get the existing evaluation result so we can append more in the infinite looping
def get_past_eval_results(evaluate_results):
    p_jokes_idx = evaluate_results['jokes_idx']
    p_guessed_ratings = evaluate_results['guessed_ratings']
    p_ratings = evaluate_results['ratings']
    p_evaluate_key = evaluate_results['evaluate_key']
    return p_jokes_idx, p_guessed_ratings, p_ratings, p_evaluate_key

# calculate label averages
def avg_ratings_by_labels(ratings, labels):
    output = [0,0,0] # median, good, bad
    num_rated = [0,0,0]
    for i,l in enumerate(labels):
        output[l] += float(ratings[i])
        num_rated[l] += 1
    for i in range(3):
        output[i] = None if num_rated[i] == 0 else output[i] / num_rated[i]
    return output

# round guessed ratings and cap at 5
def round_cap_rating(rating):
    if rating > 5:
        return '5.0'
    elif rating < 1:
        return '1.0'
    else:
        return "{0:.2f}".format(rating)

###########################################################

"""
Other fun things for people to play with
"""
@myapp.route('/funny_jokes', methods=['GET', 'POST'])
def funny_jokes():
    result = json.loads(session['result'])
    jokes_idx, jokes_txt, jokes_rating = models.get_good_jokes(result)
    if jokes_idx is None:
        return render_template('completion.html')

    for i in jokes_idx:
        result[str(i)] = 'None'
    session['result'] = json.dumps(result)
    return render_template('funny.html', jokes = jokes_txt)

###########################################################

# last page
@myapp.route('/completion', methods=['GET','POST'])
def completion():
    session.pop('page', None)
    session.pop('baseline_result', None)
    session.pop('result', None)
    return render_template('completion.html')

# unused at the moment - good for cross-checking and validation
@myapp.route('/results', methods=['GET','POST'])
def results():
    result = json.loads(session['result'])
    return render_template('results.html', result = result)
