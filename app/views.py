from app import myapp, models
from flask import render_template, redirect, request, session, url_for, escape, flash
from .forms import QuestionForm, EvaluateForm
import requests, json, re, datetime
from time import time
import numpy as np

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
	return render_template('update.html')

@myapp.route('/recommendation', methods=['GET','POST'])
def recommendation():
	result = json.loads(session['result'])
	error = None

	# TODO: Update in the future if anything changes
	jokes_idx, jokes_text, guessed_ratings = models.get_top_five_jokes(result)

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
			return render_template('recommendation.html',
			error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)

		# result: a dictionary of joke ID: user rating so far
		for i in range(len(ratings)):
			result[str(jokes_idx[i])] = ratings[i]

		session['result'] = json.dumps(result)

		# writing user's response into json file
		filename = session['filename']
		models.write_response_to_json(filename, result)

		# TODO: some dark ML magic should happen here!
		return redirect('/recommendation')

	return render_template('recommendation.html',
	error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)


def recommended_jokes(joke_getter):
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
			return render_template('recommendation.html',
			error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)

		# result: a dictionary of joke ID: user rating so far
		for i in range(len(ratings)):
			result[str(jokes_idx[i])] = ratings[i]

		session['result'] = json.dumps(result)

		# writing user's response into json file
		filename = session['filename']
		models.write_response_to_json(filename, result)

		# TODO: some dark ML magic should happen here!
		return redirect('/recommendation')

	return render_template('recommendation.html',
	error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)

@myapp.route('/goodjokes', methods=['GET','POST'])
def good_jokes():
	return recommended_jokes(models.get_good_jokes)

@myapp.route('/badjokes', methods=['GET','POST'])
def bad_jokes():
	return recommended_jokes(models.get_bad_jokes)

@myapp.route('/medianjokes', methods=['GET','POST'])
def median_jokes():
	return recommended_jokes(models.get_median_jokes)

@myapp.route('/results', methods=['GET','POST'])
def results():
	result = json.loads(session['result'])
	return render_template('results.html', result = result)

@myapp.route('/evaluate', methods=['GET','POST'])
def evaluate():
	result = json.loads(session['result'])
	error = None

	# TODO: Update in the future if anything changes
	models_list = [models.get_good_jokes(result), models.get_median_jokes(result), models.get_bad_jokes(result)]
	indices, texts, ratings = [], [], []
	for model in models_list:
		indices += model[0]
		texts += model[1]
		ratings += model[2]
	print(indices)
	print(texts)
	print(ratings)

	shuffled_indices = np.arange(15)
	np.random.shuffle(shuffled_indices)
	# tells you which jokes are good(1), bad(-1), median(0)

	evaluate_key = (shuffled_indices < 5).astype(int) + -1*(shuffled_indices > 9).astype(int)
	jokes_idx, jokes_text, guessed_ratings = [], [], []
	for index in shuffled_indices:
		jokes_idx.append(int(indices[index]))
		jokes_text.append(texts[index])
		guessed_ratings.append(ratings[index]) 

	if jokes_idx is None:
		error = 'This is embarrassing - we are having some backend issues at the moment, please check back later'

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
		for i in range(len(ratings)):
			result[str(jokes_idx[i])] = ratings[i]

		session['result'] = json.dumps(result)
		session['evaluateresults'] = json.dumps({'jokes_idx':jokes_idx, 'jokes_text':jokes_text, 'guessed_ratings':guessed_ratings, 'ratings':ratings, 'evaluate_key':evaluate_key.tolist()})

		# writing user's response into json file
		filename = session['filename']
		models.write_response_to_json(filename, result)

		# TODO: some dark ML magic should happen here!
		return redirect('/evaluateresults')

	return render_template('recommendation.html',
	error=error, jokes = jokes_text, ratings = guessed_ratings, form = form)

@myapp.route('/evaluateresults', methods=['GET','POST'])
def evaluateresult():
	evaluateresult = json.loads(session['evaluateresults'])
	error = None

	jokes_idx, jokes_text, guessed_ratings = evaluateresult['jokes_idx'], evaluateresult['jokes_text'], evaluateresult['guessed_ratings']
	ratings, evaluate_key = evaluateresult['ratings'], evaluateresult['evaluate_key'] 
	if jokes_idx is None:
		error = 'This is embarrassing - we are having some backend issues at the moment, please check back later'
	
	# calc avgs
	def avg_ratings_by_labels(ratings, labels):
		print('here are labels', labels)
		output = [0,0,0]
		for i,l in enumerate(labels):
			output[l] += float(ratings[i])
		for i in range(3):
			output[i] /= 5.0
		return output
	avgs = avg_ratings_by_labels(ratings, evaluate_key)
	good_avg, median_avg, bad_avg = avgs[1], avgs[0], avgs[-1]
	form = EvaluateForm()

	# convert numeric labels to strings
	groups = []
	for l in evaluate_key:
		if l == 0:
			groups.append('median')
		if l == 1:
			groups.append('good')
		if l == 0:
			groups.append('bad')

	# round guessed ratings and cap at 5
	def round_cap_rating(rating):
		if rating > 5:
			return '5.0'
		else:
			return "{0:.2f}".format(rating)

	rounded_ratings = list(map(round_cap_rating, guessed_ratings))
	print(rounded_ratings)

	return render_template('evaluateresults.html',
	error=error, jokes = jokes_text, ratings=ratings, group=groups, guessed_ratings = rounded_ratings, form = form, good_avg=good_avg, bad_avg=bad_avg, median_avg=median_avg)