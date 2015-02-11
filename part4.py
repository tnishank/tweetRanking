import sys
import simplejson
import difflib
from collections import defaultdict
import re
from collections import Counter
import math
import unicodedata
import codecs
from  tweet import Tweet
from stemming.porter2 import stem
import tweet

tfdict = defaultdict(int)
idfdict = defaultdict(int)
TotalTweets = 0.0
tweetObjectdict = {}
dictdocIDNormalized = defaultdict(int) # mapping of docid and its normailzed value

def ParseTweet():
	global idfdict,tfdict,tweetObjectdict
	f = file('m.json', "r")
	#f = file('test.json',"r")
	i =0.0
	lines = f.readlines()
	#tweetObjectdict = {}
        for line in lines:
			try:
				tweet = simplejson.loads(unicode(line),encoding="UTF-8")
				t1 = Tweet()
				t1.loadtweet(tweet,tfdict)
				tweetObjectdict[t1.tid] = t1
				i = i+1
			except ValueError:
				pass
	global TotalTweets
	TotalTweets = i
	return tweetObjectdict
def PageRank():
	for key in tweet.dictInlink:
		if not tweet.dictOutlink.has_key(key):
			tweet.dictOutlink[key] =  set()
			
	N = len(tweet.dictOutlink)
	#print "NUmber of users %s"%N
	oldRank = {}
	d = 0.9
	for user in tweet.dictOutlink:
		oldRank[user] = 1.0/
	isContinue = True
	i = 0
	while(isContinue):
		newRank = {}
		isContinue = False
		for user in tweet.dictOutlink:
			rank = (1-d)/N
			userlist = []
			userlist = tweet.dictInlink[user]
			for node in userlist:
				userlen = len(tweet.dictOutlink[node])
				if userlen == 0:
					userlen = 1		
				rank = rank + d*(oldRank[node]/userlen)
			newRank[user] = rank
		if(oldRank[user] - newRank[user] >= 0.0001):
			isContinue = True
		oldRank = newRank
		i = i+1
		#print "Iteration %s complete"%i
		#break
	#print "Number of Iteration done : %s "%i
	return oldRank