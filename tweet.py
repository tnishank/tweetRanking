import sys
import simplejson
import difflib
from collections import defaultdict
import re
from collections import Counter
import math
from stemming.porter2 import stem

dictUserID = {}  # Mapping of Username with their Tweet given ID
dictOutlink = defaultdict(set) # Mapping of User Name with their Mention Name # Basically Outlink Dictionary
dictInlink  = defaultdict(set) # Mapping of User Name with Users who mention this user # Basically Inlink Dictionary 
dictIDMap = defaultdict() # Mapping of Self Generated ID to Tweet given ID and User Name and mention name
dictUserdoc = defaultdict()
dicthashtag = defaultdict()
dictUserNotTag = defaultdict()
usernumber = 0
class Tweet():
	#globalworddict = defaultdict(int) #stores term and id
	global dictUserID 
	global dictInlink
	global dictOutlink
	global dictIDMap
	global dictUserdoc
	global dicthashtag
	global dictUserNotTag
	def __init__(self):
		self.tid = None
		self.text = None
		self.wordfreq = {} # [term] = frequency
		self.nwordfreq = {} # [term] = normailzed tf
		self.wordlist = []
		self.tuser = None
		self.tuser_mention = {}

	def loadtweet(self,tweet,tfdict):
		
		global usernumber
		self.tid = tweet["id"]
		self.text = tweet["text"].lower()
		self.wordlist = re.findall(r"[\w']+",self.text)
		self.wordfreq = Counter(self.wordlist)
		
		for w,freq in (self.wordfreq).items():
			dict1 = {}
			word = (str(w))
			#self.nwordfreq[word] = 1 + math.log(freq,2) #base log2
			dict1[tweet['id']] = 1+ math.log(freq,2)
			tfdict.setdefault(stem(word),[]).append(dict1)
		
		self.user = tweet['user']
        	self.tuser = str(self.user["screen_name"])
		username = str(self.user['screen_name']).lower()
		dictUserID[tweet['id']] = username
		dictIDMap[username] = tweet['id']
		entities = tweet["entities"]
		#present = False
		hashtaglist = []
		dictUserdoc.setdefault(username,[]).append(self.tid)
		selfcount = 0
		if entities:
			mentionlist = entities.get('user_mentions')
			mlen = len(mentionlist)
			if  mlen != 0:
               			for items in entities.get("user_mentions"):
						mentionname = str(items["screen_name"]).lower()	
						if mentionname != username:
							self.tuser_mention[items["id"]] = mentionname #tweet object entry			
							dictOutlink[username].add(mentionname)
							dictInlink[mentionname].add(username)
			
			#calculating hashtags
			
		
			hashtaglist = entities.get("hashtags")
			if not len(hashtaglist) == 0:
				#print "length is : %s and list is: %s"%(len(hashtaglist),hashtaglist)
				for item in hashtaglist:
					#print item
					tag = item['text'].lower()		
					dicthashtag.setdefault(tag,[]).append(username)
			else:
				textlist = self.wordlist
				dictUserNotTag.setdefault(username,[]).append(textlist)

					

	def tprint(self):
		print "ID            : %s" %self.tid
		print "text          : %s" %self.text
		print "wordfreq      : %s" %self.wordfreq
		print "nwordfreq     : %s" %self.nwordfreq
		print "tweet users   : %s" %self.tuser
		print "user_mentions : %s" %self.tuser_mention

