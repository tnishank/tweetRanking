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
import tweet
import operator
from datetime import datetime

tfdict = defaultdict(int)
idfdict = defaultdict(int)
TotalTweets = 0
tweetObjectdict = {}
dictdocIDNormalized = defaultdict(int) # mapping of docid and its normailzed value

def ParseTweet():
	global idfdict,tfdict,tweetObjectdict
	# Loop over all lines
	f = file('m.json', "r")
	#f = file('test.json',"r")
	i =0
	lines = f.readlines()
	#tweetObjectdict = {}
	for line in lines:
		try:
			tweet = simplejson.loads(unicode(line),encoding="UTF-8")
			#print tweet
			t1 = Tweet()
			t1.loadtweet(tweet,tfdict)
			tweetObjectdict[t1.tid] = t1
			i = i+1
		except ValueError:
			print "Can't parse the tweet"
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
		oldRank[user] = 1.0/N
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
			if(oldRank[user] - newRank[user] >= 0.00001):
				isContinue = True
		oldRank = newRank
		i = i+1
		#print "Iteration %s complete"%i
		#break
	#print "Number of Iteration done : %s "%i
	return newRank

def main():
	tweetlist = ParseTweet()
	rank = PageRank()
	global idfdict,tfdicttweetObjectdict,dictdocIDNormalized
	#print "\n\nUser               ============>>  PageRank"
	#print"===============================================\n"
	k =0
	#rk = sorted(rank,key = rank.get,reverse = True)
	#for w in rk:
	for w in sorted(rank,key = rank.get,reverse = True):
		#print "%s:          %s" %(w,rank[w])
		k =  k+1
		print '{0:5} : {1:15}   ============>> {2:10f}'.format(k,w,rank[w])
		#print 'Rank:{0:2}:  :{1:10}'.format(k,w)
		if k == 50:
			break
	
if __name__ == '__main__':
	main()
