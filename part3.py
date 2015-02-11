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
import random

tfdict = defaultdict(int)
idfdict = defaultdict(int)
TotalTweets = 0.0
tweetObjectdict = {}
dictdocIDNormalized = defaultdict(int) # mapping of docid and its normailzed value

def ParseTweet():
	global idfdict,tfdict,tweetObjectdict
	# Loop over all lines
	f = file('m.json', "r")
	#f = file('test.json',"r")
	i =0.0
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
			pass
	global TotalTweets
	TotalTweets = i
	return tweetObjectdict


def calculateIDF(tweetlist):
	global idfdict,tfdict,tweetObjectdict
	#print "***************  Now calculate idf *****************\n"
	idfdict = defaultdict(int)
	j = 0
	global TotalTweets		
	#print "TotalTweets are : %s" %TotalTweets
	for key,value in sorted(tfdict.iteritems(),key = lambda(k,v) : (v,k)):
		j = j+1	
		#print "%s : %s" %(key,value)
		doclist = value
		docfreq = len(doclist)
		#print "docfreq is: %s and total docs are : %s" %(docfreq,TotalTweets)
		try:
			idf = math.log(TotalTweets/docfreq,2)
			#print "idf value for word : %s is : %s" %(key,idf)
			idfdict[key] = idf
		except ValueError:
			print "error in calculating log"	
		j = j+1

def calculateTFIDF():

	global idfdict,tfdict,tweetObjectdict,normValdoc
	#print "\n**************** TFIDF **********************\n\n"
	for key in tfdict.iterkeys():	
		#print "word is %s"%key
		idfweight  = idfdict[key]
		#print" idfweight is : %s" %idfweight
		doclist = tfdict[key]
		
		for docid in doclist:	
			for item in docid.iterkeys():
				docid[item] = docid[item] * idfweight
				#print "new value tfidf in %s %s %s"%(key,item,docid[item])

def getdocnormalized():
	global idfdict,tfdict,dictdocIDNormalized
	for key in tfdict.iterkeys():
		doclist = tfdict[key]
		for docid in doclist:
			for item in docid.iterkeys():
				dictdocIDNormalized[item]  = dictdocIDNormalized[item] + docid[item]* docid[item]
	
def MaxUserCosValue(cosval):
	MaxCosVal = {}
	for user in tweet.dictUserdoc:
		cosvaluelist = []
		for docid in tweet.dictUserdoc[user]:
			if cosval.has_key(docid):
				cosvaluelist.append(cosval[docid])
		if len(cosvaluelist):
			MaxCosVal[user] = max(cosvaluelist)
		else:
			MaxCosVal[user] = 0
	#print "********MaxCosVal:*****%s\n"%MaxCosVal
	return MaxCosVal


def Part3PageRank(MaxCosVal):

	for key in tweet.dictInlink:
		if not tweet.dictOutlink.has_key(key):
			tweet.dictOutlink[key] =  set()
	N = len(tweet.dictOutlink)
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
				if not MaxCosVal.has_key(node):
					MaxCosVal[node] = 0
				rank = rank + d *(oldRank[node]/userlen) * MaxCosVal[node] 
			newRank[user] = rank
			if (oldRank[user] - newRank[user] >= 0.00001):
				isContinue = True
		oldRank = newRank
		i = i+1
		#break
	return newRank	  

def main():

	tweetlist = ParseTweet()	
 	calculateIDF(tweetlist)	
	calculateTFIDF()
	getdocnormalized()

	print "\n\n******* Enter Query To Search *********\n"
	stdinput = raw_input()
	
	while(stdinput != 'quit'):
		if(stdinput == ''):
			print "\n*************** Invalid Query: Reason:Empty Query ****************\n"
			print "\n\n*************** Enter String to Search ****************\n\n"
			stdinput = raw_input()
			continue
		ulist = [] # union of list of docs for each query term
		qwordlist = re.findall(r"[\w']+",(stdinput.lower()))
		qwordfreq = Counter(qwordlist)
		querydict = {}
		isContinue = 1
		for word in qwordfreq:
			freq = 0.0
			freq = float(qwordfreq[word])
			querytf  = (1+ math.log(freq,2))
			#print querytf
			if word in idfdict.keys():
				queryidf = idfdict[word]
			else:
				print "Sorry, IDF undefined. All words are not in tweet corpus."
				isContinue = 0
				break
			#print "query idf is : %s "%queryidf
			querydict[word] = (querytf * queryidf)
		if not isContinue:
			print "\n*********Enter Query to search********\n"
                	stdinput = raw_input()
			continue

		#caluculate cosine similarity now
		cosval = {}
		tfidfdoclist = []		
		#print "======================== Dangerous =============================================="
		qsum = defaultdict(int)
		qsqsum = defaultdict(int)
		dsqsum = defaultdict(int)
		newdoclist = {}
		for word in qwordfreq:
			#print "word is %s" %word
			tfidfdoclist = tfdict[word]
			#print "tfidfdoclist of word is %s and len is %s" %(len(tfidfdoclist),tfidfdoclist)
			for item in tfidfdoclist:
				for key in item:
					newdoclist[key] = item[key]
					qsum[key] = qsum[key] + item[key] * querydict[word]
					if not dsqsum[key]:
						dsqsum[key] = dictdocIDNormalized[key]
			#print "\n\nnew list is %s\n\n "%newlist
		for word in qwordfreq:
			for a in newdoclist:
				qsqsum[a] = qsqsum[a] + querydict[word]**2
			
		#raw_input()
			
		for docid in newdoclist:
			if qsqsum[docid]:
				cosval[docid]  = qsum[docid]/(math.sqrt(qsqsum[docid]) * math.sqrt(dsqsum[docid]))
				#print "cosval is *************************** %s" %cosval
			else:
				cosval[docid] = 0
		#print cosval
		

		MaxCosVal = MaxUserCosValue(cosval)
		rank3 = Part3PageRank(MaxCosVal)
		#rank = PageRank()
			
		print"============== Query Based Rank ===============================\n"
		k=0
		querydepRank = {}
		for w in sorted(rank3,key = rank3.get,reverse = True):
		#print "%s:          %s" %(w,rank[w])
			k =  k+1
			querydepRank[w] = k
			#print '{0:5} : {1:15}   ============>> {2:10f}'.format(k,w,rank[w])
			print 'Rank:{0:2}:  :{1:10}: {2:1}'.format(k,w,rank3[w])          
			if k == 10:
				break
                #print "querdeprank************\n %s" %querydepRank
	
		print"============== Query Based Result ===============================\n"
		for key in cosval:
			user = tweet.dictUserID[key]
			if cosval.has_key(key):
				if not  querydepRank.has_key(user):
					#print "No Value"
					querydepRank[user] = random.randrange(47933,66000)
				
				cosval[key] = cosval[key] * 1.000000/(1+math.log(querydepRank[user],2))
			else:
				cosval[key] = 0

		#print "\n\nFor query : %s" %stdinput
		#print "\nTweet Id : Cosine Value\n"i
		
		k=1
		print "\n************************** Query Based RESULT *****************************\n\n"
		for key,value in sorted(cosval.iteritems(),key = lambda(k,v) : (v,k),reverse = True):
			#print "%s :%s : %s : %s" %(k,key,value,tweetObjectdict[key].text)
			print "[%s]:[Cosval: %s]: Tweet: [%s]" %(k,value,tweetObjectdict[key].text)
			k = k+1
			if k ==11:
				break
		print "\n*********Enter Query to search********\n"
		
		stdinput = raw_input()


if __name__ == '__main__':
 main()
