from app import myapp, models
from flask import render_template, redirect, request, session, url_for, escape, flash
from .forms import ExampleForm
import requests, json, re, datetime

"""
View functions:
* Handle logic on the front-end
* Access the models file to use SQL functions
"""

# landing redirect
@myapp.route('/')
@myapp.route('/index')
def index():
	return render_template('welcome.html')

# display some random jokes
@myapp.route('/jokes', methods=['GET','POST'])
def jokes():
	jokes_df = models.get_random_jokes()
	jokes_idx = list(jokes_df.index)
	jokes_text = list(jokes_df['text'])

	session['result'] = None
	ratings = []

	form = ExampleForm()
	if form.validate_on_submit():
		for field in form:
			ratings += [field.data]

		# first field is CSRF field - remove that from the output
		ratings = ratings[1:]

		# store result as a joke ID: rating pair in session
		result = dict()
		for i in range(len(ratings)):
			result[str(jokes_idx[i])] = ratings[i]

		result_string = str(json.dumps(result))
		session['result'] = result_string

		return redirect('/results')

	return render_template('jokes.html', jokes = jokes_text, joke_ids = jokes_idx, form = form)

@myapp.route('/results')
def results():
	result_string = session['result']
	print('result string 2', result_string)
	result = json.loads(result_string)
	return render_template('results.html', result = result)
