from bs4 import BeautifulSoup
import urllib
import pandas as pd
# =============================
# functions for onelinefun.com
# =============================
def get_jokes_on_page(url):
	"""gets the jokes as raw BeautifulSoupTag on a given page's url"""
	r = urllib.request.urlopen(url).read()
	soup = BeautifulSoup(r, 'lxml')
	return soup.find_all(class_='oneliner')

def convert_raw_joke(joke):
	"""convert joke to form [text, ratingVal, ratingCount, [tags]]"""
	return [joke.p.string, joke.find(itemprop='ratingValue').string,
		joke.find(itemprop='ratingCount').string, ', '.join([t.string for t in joke.find('span', class_='links').find_all('a')])]


def convert_raw_jokes(joke_list):
	return [convert_raw_joke(j) for j in joke_list]

output = None
for i in range(1, 281):
	jokes = get_jokes_on_page('http://onelinefun.com/{}/'.format(i))
	converted_jokes = convert_raw_jokes(jokes)
	joke_df = pd.DataFrame.from_records(converted_jokes, columns=['text', 'ratingVal', 'ratingCount', 'tags'])
	try:
		print(joke_df)
	except:
		print("unprintable character, but don't worry")

	if output is None:
		output = joke_df
	else:
		output = output.append(joke_df)
output.to_csv('./onelinefun.csv')
