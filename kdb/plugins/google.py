"""Google

Googles stuff.
"""

__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import re
import urllib

from kdb.plugin import BasePlugin

class Google(BasePlugin):
	"""Google Plugin

	Google stuff
	Usage: .google [-d<results> ]<search terms>
	"""

	data = ""

	def cmdGoogle(self, source, search):
		m = re.search(r"(?:-(?:d|r)(\d{1,}) )?(.+)",search,re.IGNORECASE)
		if not m:
			msg = 'Usage: .google [-d<results> ]<search terms>'
			return msg
		searchfor = m.group(2)
		results = m.group(1)
		msg = []

		if results:
			results = int(results)
			if results < 1:
				results = 1
		if not results:
			results = 1
		if results > 8:
			results = 8

		try:
			 data = urllib.urlopen('http://www.google.com/uds/GwebSearch?callback=GwebSearch.RawCompletion&context=0&lstkp=0&hl=en&key=ABQIAAAAeBvxXUmueP_8_kTINo0H4hSKL4HoBFFxfS_vfvgFpLqAt5GPWRTHDAESci2RYvZRkcpsYXapXjZWKA&v=1.0&rsz=large&q='+urllib.quote(searchfor)).read()
		except IOError: 
			 msg = "Can't connect to google!"
			 return msg
		data = uni(data)
		m = re.search('estimatedResultCount":"([^"]+)"',data)
		matches = m.group(1)
		m = re.findall(r'"url":"([^"]*)".*?"titleNoFormatting":"([^"]*)","content":"([^"]*)"',data,re.IGNORECASE)
		if m:
			if len(m) < int(results):
				results = len(m)
			if results == 1:
				msg.append(chr(2)+rh(m[0][1])+chr(2)+' - ( '+chr(31)+m[0][0]+chr(31)+' ) ['+matches+' matches]')
				msg.append(rh(m[0][2]))
			else:
				msg.append('Showing the first '+chr(2)+str(results)+chr(2)+' of '+chr(2)+str(matches)+chr(2)+' matches')
				for x in range(results):
					msg.append(chr(2)+rh(m[x][1])+chr(2)+' - ( '+chr(31)+m[x][0]+chr(31)+' )')
		else:
			 msg.append('Didn\'t find anything!')

		return msg



def uni(s):
	"converts \uXXXX in s to their ascii counterparts"
	ret = ""
	i = 0
	while i < len(s):
		if s[i:i+2] == "\u":
			x = int(s[i+2:i+6],16)
			if x < 256:
				ret += chr(x)
			i += 6
		else:
				ret += s[i]
				i+=1
	return ret


def rh(s):
	#remove html and other crap
	s = htmldecode(s)
	s = re.sub("<[^>]+>","",s)
	s = re.sub(" +"," ",s)
	return s

#decode.py
entity_sub = re.compile(r'&(#(\d+|x[\da-fA-F]+)|[\w.:-]+);?').sub
def uchr(c):
	if not isinstance(c, int):
		return c
	if c>255: return unichr(c)
	return chr(c)

def decode_entity(match):
	what = match.group(1)
	if what.startswith('#x'):
		what = int(what[2:], 16)
	elif what.startswith('#'):
		what = int(what[1:])
	else:
		from htmlentitydefs import name2codepoint
		what = name2codepoint.get(what, match.group(0))
	return uchr(what)

def htmldecode(text):
	"Decode HTML entities in the given text."
	return entity_sub(decode_entity, text)
