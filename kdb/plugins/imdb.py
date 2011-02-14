"""IMDB

Looks up information about a movie on IMDB.com.
"""

__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"

import string
import urllib
import re

from kdb.plugin import BasePlugin

class IMDB(BasePlugin):
    """IMDB Plugin

    Looks up information about a movie on IMDB.com.
    See: commands imdb
    """
    data = ""

    def cmdIMDB(self, source, target, movie):
        """Resolve the given hostname/ip
        
        Syntax: IMDB <movie>
        """
        imdburl = "http://www.imdb.com/find?s=tt&q="
        match = re.search(r"(.+?)(?: \(?(\d{4})\)?)?$",movie)
        global data
        
        
        movie = match.group(1).strip(" ")
        try:
            data = urllib.urlopen(imdburl+urllib.quote(movie)).read()
        except IOError: 
            msg = "Can't connect to imdb!"
            return msg
        
        m = re.search(r"<title>IMDB[^<]+Search<\/title>", data, re.IGNORECASE)
        if m:
            msg = self.imdbsearch(match)
        else:
            if len(data) == 0:
                headers = urllib.urlopen(imdburl+urllib.quote(movie)).info()
                if not isinstance(headers, list): 
                    headers = dict(headers)
                    headers['Status'] = '200'
                else: 
                    newheaders = dict(headers[0])
                    newheaders['Status'] = str(headers[1])
                    headers = newheaders
                if headers.has_key("location"):
                    try:
                        data = urllib.urlopen(headers.get("location")).read()
                    except IOError: 
                        msg = "Can't connect to imdb!"
                        return msg

                    msg = self.imdbparse(0)
                else:
                    msg = "Broken head!"
                    return msg
            else:
                msg = self.imdbparse(0)

        return msg

    def imdbparse(self, url):
        global data
        result = []
        
        if not url:
            m = re.search(r"pro\.imdb\.com(/title/tt\d{7}/)", data, re.IGNORECASE)
            if m:
                url = m.group(1)
            else:
                msg = "Something went wrong!"
                return msg
            
        m = re.search(r"<title>([^<]+?)<\/title>", data, re.IGNORECASE)
        if m:
            result.append(chr(2)+htmldecode(m.group(1))+chr(2)+" - [ "+chr(31)+"http://www.imdb.com"+url+chr(31)+" ]")
        else:
            msg = "Something went wrong"
            return msg
    
        m = re.findall(r"<a href=\"/Sections/Genres/[a-zA-Z\-0-9]+/\">([a-zA-Z\-0-9.]+)</a>",data)
        if m:
            genre = ""
            for x in m:
                genre += " / "+x
            result.append(chr(2)+"Genre:"+chr(2)+" "+genre[3:])
    
        m = re.search(r">((?:Top 250|Bottom 100):[^<]+)</a>", data, re.IGNORECASE)
        bottomtop = ""
        if m:
            bottomtop = " ["+m.group(1)+"]"
    
        m = re.search(r"\(awaiting 5 votes\)", data, re.IGNORECASE)
        if m:
            result.append(chr(2)+"Rating:"+chr(2)+"Awaiting 5 votes.")
        else:
            m = re.search(r"<b>User rating:</b>\s*?<b>([^<]*?)</b>", data, re.IGNORECASE)
            if m:
                m2 = re.search(r"<a href=\"ratings\">([^<]*?) votes<\/a>", data, re.IGNORECASE)
                if m2:
                    votes = " ("+m2.group(1)+" votes)"
                else:
                    votes = ""
                result.append(chr(2)+"Rating:"+chr(2)+" "+m.group(1)+votes+bottomtop)
    
        m = re.search(r"Plot (?:Outline|Summary):</h5>([^<]*?)<", data, re.IGNORECASE)
        if m:
            result.append(chr(2)+"Plot:"+chr(2)+" "+htmldecode(m.group(1).replace("\n","").replace("\r","").strip(" ")))

        m = re.search(r"Tagline:</h5>([^<]*?)<", data, re.IGNORECASE)
        if m:
            result.append(chr(2)+"Tagline:"+chr(2)+" "+htmldecode(m.group(1).replace("\n","").replace("\r","").strip(" ")))
    
        m = re.search(r"Release Date:</h5>([^<]*?)<", data, re.IGNORECASE)
        if m:
            result.append(chr(2)+"Release:"+chr(2)+" "+htmldecode(m.group(1).replace("\n","").replace("\r","").strip(" ")))
    
        m = re.search(r"Runtime:</h5>([^<]*?)<", data, re.IGNORECASE)
        if m:
            result.append(chr(2)+"Runtime:"+chr(2)+" "+htmldecode(m.group(1).replace("\n","").replace("\r","").strip(" ")))
    
        m = re.findall(r'<a href="/Sections/Countries/[^"]+">([^<]+)</a>',data)
        if m:
            country = ""
            for x in m:
                country += " / "+x
            result.append(chr(2)+"Country:"+chr(2)+" "+country[3:].strip(" "))
    
        m = re.findall(r'<a href="/Sections/Languages/[^"]+">([^<]+)</a>',data)
        if m:
            language = ""
            for x in m:
                language += " / "+x
            result.append(chr(2)+"Language:"+chr(2)+" "+language[3:].strip(" "))
    
        m = re.search(r"User Comments:</h5>([^<]*?)<", data, re.IGNORECASE)
        if m:
            result.append(chr(2)+"User Comments:"+chr(2)+" "+htmldecode(m.group(1).replace("\n","").replace("\r","").strip(" ")))
            
        return result
    
    def imdbsearch(self, match):
        global data
    
        movie = match.group(1).strip(" ")
        year = match.group(2)

        regex = []
        if year:
            regex.append(r"<a href=\"(\/title\/tt\d{7}\/)\">("+movie+")</a> \("+year+"\)")
            regex.append(r"<a href=\"(\/title\/tt\d{7}\/)\">("+movie+", The)</a> \("+year+"\)")
            regex.append(r"<a href=\"(\/title\/tt\d{7}\/)\">(\""+movie+"\")</a> \("+year+"\)")
            regex.append(r"<a href=\"(\/title\/tt\d{7}\/)\">([^<]*?"+movie+"[^<]*?)</a> \("+year+"\)")
            regex.append(r"<a href=\"(\/title\/tt\d{7}\/)\">([^<]*?)</a> \("+year+"\)")
        regex.append(r"<a href=\"(\/title\/tt\d{7}\/)\">("+movie+")</a>")
        regex.append(r"<a href=\"(\/title\/tt\d{7}\/)\">("+movie+", The)</a>")
        regex.append(r"<a href=\"(\/title\/tt\d{7}\/)\">(\""+movie+"\")</a>")
        regex.append(r"<a href=\"(\/title\/tt\d{7}\/)\">([^<]*?"+movie+"[^<]*?)</a>")
        regex.append(r"<a href=\"(\/title\/tt\d{7}\/)\">([^<]*?)</a>")
    
        for x in regex:
            m = re.search(x, data, re.IGNORECASE)
            if m:
                try:
                    data = urllib.urlopen("http://www.imdb.com"+m.group(1)).read()
                except IOError: 
                    msg = "Can't connect to imdb!"
                    return msg
                msg = self.imdbparse(m.group(1))
                break
        if not m:
            msg = "Your search returned no matches"
        return msg


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
