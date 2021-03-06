from model.Tweet import Tweet
import tweepy
import os
import json
from service.Listener import Listener
import app
from flask import session
import sqlite3

"""
Controller handling requests from the Router. Creates a sqllite database if is not existing. Provides basic table 
structur.
"""
class TweetController(object):

	def __init__(self, server):		
		self.auth = tweepy.OAuthHandler(app.config["consumer_key"], app.config["consumer_secret"])
		self.auth.set_access_token(app.config["access_token"], app.config["access_token_secret"])
		self.api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())
		self.server = server
		self.conn = sqlite3.connect(os.path.dirname(__file__)  + "/../../iscp.db", check_same_thread=False)
		self.create_table_if_not_exist()

	def start_stream(self, keywords):
		"""
		Start a Twitter stream and analyse incoming tweets.
		"""
		self.reset_status()
		self.set_status("active")
		self.tweet_listener = Listener(app = self.server)
		self.stream = tweepy.Stream(auth = self.auth, listener=self.tweet_listener)
		self.stream.filter(track=keywords, async=True)

	def stop_stream(self):
		"""
		Stop the Twitter stream and sentiment analysis.
		"""
		self.set_status("inactive")

	def set_status(self, status):
		"""
		Set the given status in the database.
		"""
		cursor = self.conn.cursor()
		cursor.execute("UPDATE stream_status SET status=? WHERE id = 1", (status,))
		self.conn.commit()

	def get_status(self):
		"""
		Retrieve the current status from the database (id, status, tweets_analyzed, avg_mood, pos_tweets, neg_tweets, 
		neu_tweets).
		"""
		cursor = self.conn.cursor()
		cursor.execute("SELECT * FROM stream_status WHERE id = 1")
		result = cursor.fetchall()
		return result[0]

	def create_table_if_not_exist(self):
		"""
		If stream_status table doesn't exist create it and fill it with data.
		"""
		cursor = self.conn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS `stream_status` (`id` INTEGER PRIMARY KEY AUTOINCREMENT,`status`	TEXT,`tweets_retrieved`	INTEGER,`avg_mood` TEXT, `pos_tweets` INTEGER, `neg_tweets` INTEGER, `neu_tweets` INTEGER)")
		cursor.execute("INSERT OR IGNORE INTO `stream_status`(`id`, `status`, `tweets_retrieved`,`avg_mood`, `pos_tweets`, `neg_tweets`, `neu_tweets`) VALUES(1, 'inactive', 0, 'neu', 0, 0, 0)")
		self.conn.commit()

	def reset_status(self):
		"""
		Reset the current status.
		"""
		cursor = self.conn.cursor()
		cursor.execute("UPDATE stream_status SET tweets_retrieved=?, avg_mood=?, pos_tweets=?, neg_tweets=?, neu_tweets=? WHERE id = 1", (0, 'neu', 0, 0, 0,))
		self.conn.commit()		
