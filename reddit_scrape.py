import praw
from pprint import pprint
import pandas as pd

def get_all_posts(lim=1000, sort_by='top', subreddit_name='jokes'):
	r = praw.Reddit(user_agent='joke_scraper')
	if sort_by == 'top':
		submissions = r.get_subreddit(subreddit_name).get_top_from_all(limit=lim)
	elif sort_by == 'controversial':
		submissions = r.get_subreddit(subreddit_name).get_controversial(limit=lim)
	elif sort_by == 'hot':
		submissions = r.get_subreddit(subreddit_name).get_hot(limit=lim)
	return submissions

def submission_to_dict(post):
	"""converts a reddit post to row"""
	return {'text':'{} {}'.format(post.title, post.selftext), 'ups':post.ups, 
	'downs':post.downs, 'tag':post.link_flair_text}

def convert_posts_to_df(posts):
	df = pd.DataFrame(columns=['text', 'ups', 'downs', 'tag'])
	count = 1
	for post in posts:
		print('scraping post {}'.format(count))
		df = df.append(submission_to_dict(post), ignore_index=True)
		count += 1
	return df

# works with max 1000 posts, to get more, follow thing here 
# https://github.com/eleweek/SearchingReddit/blob/master/download_whole_subreddit.py
convert_posts_to_df(get_all_posts(lim=1000)).to_csv('./10000_reddit.csv')