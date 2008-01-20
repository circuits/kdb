"""Ep

Displays information about tv shows.
"""

__ver__ = "0.0.1"
__author__ = "liato"

import urllib
import re
import datetime as date
import time as time

from kdb.plugin import BasePlugin

class Ep(BasePlugin):
	"""EP Plugin

	View information about a tvshow
	Usage: Usage: .ep [-i ]<show>[, <season>x<episode>]
	"""
	data = ""

	def cmdEp(self, source, tvshow):
		m = re.search(r'([^,]+)(?:, ?(\d{1,3}x\d{1,3}))?',tvshow)
		if not m:
			msg = 'Usage: .ep <show>[, <season>x<episode>]'
			return msg
		show = m.group(1)
		episode = m.group(2)
		extended = 0
		result = []
		


		if show[0:2] == '-i' or show[0:2] == '-e':
			show = show[3:]
			extended = 1

		try:
			if episode:
				data = urllib.urlopen('http://www.tvrage.com/quickinfo.php?show='+urllib.quote(show)+'&ep='+urllib.quote(episode)).read()
			else:
				data = urllib.urlopen('http://www.tvrage.com/quickinfo.php?show='+urllib.quote(show)).read()
		except IOError: 
			msg = "Can't connect to tvrage!"
			return msg

		data = data.replace('\r','')
		data = data.split('\n')
		i = dict()
		for x in data:
			if '@' in x:
				i[x.split('@')[0]] = x.split('@')[1]

		if i.has_key('Show Name') and i.has_key('Show URL'):
			status=""
			if i.has_key('Status'):
				if i['Status'] == 'Canceled/Ended':
					status = ' '+chr(3)+'4(Canceled/Ended) '
			result.append(chr(2)+i['Show Name']+chr(2)+' - '+chr(31)+i['Show URL']+chr(31)+status)

			#Show info
			if not episode:
				if i.has_key('Latest Episode'):
					thisdate = time.strptime(i['Latest Episode'].split('^')[2],'%b/%d/%Y')
					datedif = str(int(float(((time.mktime(thisdate)-time.mktime(time.localtime()))/(60*60*24))))).replace('-','')
					thisdate = time.strftime("%Y-%m-%d",thisdate)
					if int(datedif) == 1:
						datedif=datedif+chr(2)+' day'
					else:
						datedif=datedif+chr(2)+' days'	
					result.append('Latest: '+chr(2)+i['Latest Episode'].split('^')[0]+chr(2)+' - '+i['Latest Episode'].split('^')[1]+' ['+thisdate+' | Aired '+chr(2)+datedif+' ago]')
				else:
					result.append('Latest: No episodes aired yet')
				if i.has_key('Next Episode'):
					thisdate = time.strptime(i['Next Episode'].split('^')[2],'%b/%d/%Y')
					datedif = str(int(float(((time.mktime(thisdate)-time.mktime(time.localtime()))/(60*60*24)))))
					thisdate = time.strftime("%Y-%m-%d",thisdate)
					if int(datedif) == 1:
						datedif=datedif+chr(2)+' day'
					else:
						datedif=datedif+chr(2)+' days'		  
					result.append('Next:   '+chr(2)+i['Next Episode'].split('^')[0]+chr(2)+' - '+i['Next Episode'].split('^')[1]+' ['+thisdate+' | Airs in '+chr(2)+datedif+']')
				else:
					result.append('Next:   No upcoming episodes')

			#Episode info
			else:
				if i.has_key('Episode Info'):
					thisdate = time.strptime(i['Episode Info'].split('^')[2],'%d/%b/%Y')
					datedif = str(int(float(((time.mktime(thisdate)-time.mktime(time.localtime()))/(60*60*24)))))
					if int(datedif) < 0:
						datedif2 = 'Aired '+chr(2)+datedif.replace('-','')+chr(2)+' day ago'
					else:
						datedif2 = 'Airs in '+chr(2)+datedif.replace('-','')+chr(2)+' day'
					thisdate = time.strftime("%Y-%m-%d",thisdate)
					if not int(datedif.replace('-','')) == 1:
						datedif=datedif2.replace('day','days')
					result.append(chr(2)+i['Episode Info'].split('^')[0]+chr(2)+' - '+i['Episode Info'].split('^')[1]+' ['+thisdate+' | '+datedif+'] - '+i['Episode URL'])
				else:
					result.append('Error:  No information about the specefied episode could be found')

			if extended:
				extinf = dict()
				extinf['header'] = 'Info:   '
				if i.has_key('Classification') or i.has_key('Premiered') or i.has_key('Network') or i.has_key('Country'):
					extinf['Classification'] = ""
					extinf['Premiered'] = ""
					extinf['Network'] = ""
					extinf['Country'] = ""
					if i.has_key('Classification'):
						extinf['Classification'] = ' '+i['Classification'].lower()
					if i.has_key('Premiered'):
						extinf['Premiered'] = ' year '+i['Premiered']
					if i.has_key('Network'):
						extinf['Network'] = ' on '+i['Network']
					if i.has_key('Country'):
						extinf['Country'] = ' in '+i['Country']
					result.append(extinf['header']+'The first episode of this'+extinf['Classification']+' show aired'+extinf['Premiered']+extinf['Country']+extinf['Network'])
					extinf['header'] = '        '
				if i.has_key('Airtime'):
					result.append(extinf['header']+'The show airs/aired on '+i['Airtime'].lower().split(',')[0]+'s, '+i['Airtime'].split(',')[1])
					extinf['header'] = '        '
				if i.has_key('Status'):
					extinf['Genres'] = ""
					if i.has_key('Genres'):
						extinf['Genres'] = ' and the genre(s) are '+i['Genres'].replace(' | ',', ').lower()
					result.append(extinf['header']+'The current status of the show is "'+i['Status'].lower()+'"'+extinf['Genres'])
						
		else:
			result.append('The show could not be found :(')
		return result
