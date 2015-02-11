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

def calculateIDF(tweetlist):
	global idfdict,tfdict,tweetObjectdict
	#print "***************  Now calculate idf *****************\n"
	idfdict = defaultdict(int)
	j = 0
	global TotalTweets		
	#print "TotalTweets are : %s" %TotalTweets
        for key,value in sorted(tfdict.iteritems(),key = lambda(k,v) : (v,k)):
			j = j+1
			doclist = value
			docfreq = len(doclist)
                #print "docfreq is: %s and total docs are : %s" %(docfreq,TotalTweets)
			try:
				idf = math.log(TotalTweets/docfreq,2)#
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
		#print qwordlist
		qwordfreq = Counter(qwordlist)
		#print qwordfreq
		querydict = {}
		isContinue = 1
		for word in qwordfreq:
			freq = 0.0
			freq = float(qwordfreq[(word)])
			querytf = 1+ math.log(freq,2)
			#print querytf
			if stem(word) in idfdict.keys():
				queryidf = idfdict[stem(word)]
			else:
				print "Sorry, IDF undefined. All words are not in tweet corpus."
				isContinue = 0
				break
			#print "query idf is : %s "%queryidf
			querydict[stem(word)] = (querytf * queryidf)
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
			tfidfdoclist = tfdict[stem(word)]
			#print "tfidfdoclist of word is %s and len is %s" %(len(tfidfdoclist),tfidfdoclist)
			for item in tfidfdoclist:
				for key in item:
					newdoclist[key] = item[key]
					qsum[key] = qsum[key] + item[key] * querydict[stem(word)]
					if not dsqsum[key]:
						dsqsum[key] = dictdocIDNormalized[key]
		for word in qwordfreq:
			for a in newdoclist:
				qsqsum[a] = qsqsum[a] + querydict[stem(word)]**2
			
		#print "Done processing for query and normalization"
		
		for docid in newdoclist:
			if qsqsum[docid]:
				cosval[docid]  = qsum[docid]/(math.sqrt(qsqsum[docid]) * math.sqrt(dsqsum[docid]))
				#print "cosval is *************************** %s" %cosval
			else:
				cosval[docid] = 0
		#print cosval

		k=0
		print "\n************************** RESULT *****************************\n\n"
		for key,value in sorted(cosval.iteritems(),key = lambda(k,v) : (v,k),reverse = True):
			#print "%s :%s : %s : %s" %(k,key,value,tweetObjectdict[key].text)
			print "[%s]:[Cosval: %s] : Tweet: [%s]" %(k,value,tweetObjectdict[key].text)
			k = k+1
			if k ==50:
				break
		print "\n*********Enter Query to search********\n"
		
		stdinput = raw_input()


if __name__ == '__main__':
	main()