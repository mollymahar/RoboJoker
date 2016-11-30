from app import myapp, models
from flask import render_template, redirect, request, session, url_for, escape, flash
from .forms import QuestionForm
import requests, json, re, datetime
from time import time
import random

"""
View functions:
* Handle logic on the front-end
* Access the models file to use SQL functions
"""

# landing redirect
@myapp.route('/')
@myapp.route('/index')
def index():
	session.pop('page', None)
	session.pop('result', None)
	return render_template('index.html')

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
		result = dict() if 'result' not in session else json.loads(session['result'])
		for i in range(len(ratings)):
			result[str(jokes_idx[offset + i])] = ratings[i]

		session['result'] = json.dumps(result)

		# writing user's response into json file
		if 'filename' not in session:
			session['filename'] = 'responses/' + str(round(time())) + '.json'
		filename = session['filename']
		models.write_response_to_json(filename, result)

		# if reached last page, move onto next phase
		# otherwise increment page by 1
		if page == 4:
			return redirect('/update')
		else:
			session['page'] = str(page + 1)
			return redirect('/baseline')

	return render_template('baseline.html',
	jokes = jokes_text[offset:offset + 5], offset = offset, form = form, error = error)

@myapp.route('/update', methods=['GET','POST'])
def update():
	page_orders = ['bee', 'fish', 'octopus']
	random.shuffle(page_orders)

	session['page_1'] = page_orders[0]
	session['page_2'] = page_orders[1]
	session['page_3'] = page_orders[2]

	return render_template('update.html')

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

	# TODO: Update in the future if anything changes
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
			result[str(jokes_idx[i])] = ratings[i]

		session['result'] = json.dumps(result)

		# writing user's response into json file
		filename = session['filename']
		models.write_response_to_json(filename, result)

		# TODO: some dark ML magic should happen here!
		return redirect(next_html_handler)

	return render_template(current_html_page,
	error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)

@myapp.route('/completion', methods=['GET','POST'])
def completion():
	return render_template('completion.html')

# @myapp.route('/results', methods=['GET','POST'])
# def results():
# 	result = json.loads(session['result'])
# 	return render_template('results.html', result = result)

# @myapp.route('/recommendation', methods=['GET','POST'])
# def recommendation():
# 	result = json.loads(session['result'])
# 	error = None
#
# 	# TODO: Update in the future if anything changes
# 	jokes_idx, jokes_text, guessed_ratings = models.get_top_five_jokes(result)
#
# 	if jokes_idx is None:
# 		error = 'This is embarrassing - we are having some backend issues at the moment, please check back later'
#
# 	form = QuestionForm()
#
# 	if form.validate_on_submit():
# 		# get user ratings from form data
# 		ratings = [field.data for field in form]
# 		# first field is CSRF field - remove that from the output
# 		ratings = ratings[1:]
#
# 		if all(rating == 'None' for rating in ratings):
# 			error = 'Please rate at least 1 joke before proceeding!'
# 			return render_template('recommendation.html',
# 			error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)
#
# 		# result: a dictionary of joke ID: user rating so far
# 		for i in range(len(ratings)):
# 			result[str(jokes_idx[i])] = ratings[i]
#
# 		session['result'] = json.dumps(result)
#
# 		# writing user's response into json file
# 		filename = session['filename']
# 		models.write_response_to_json(filename, result)
#
# 		# TODO: some dark ML magic should happen here!
# 		return redirect('/recommendation')
#
# 	return render_template('recommendation.html',
# 	error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)
