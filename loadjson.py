import sys
import simplejson
import difflib
from collections import defaultdict
import re
from collections import Counter
import math
import unicodedata
import codecs
import json

def extract_tweet():
	try:
		f = file('t.json',"r")
		lines = f.readlines();
		for line in lines:
			tweet = simplejson.loads(unicode(line),encoding="UTF-8")
			#print tweet
			#i = raw_input()
	except ValueError:
		print 'can not open file'
extract_tweet()