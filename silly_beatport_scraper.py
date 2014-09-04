"""
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
"""

"""
Beatport has locked up their API, making it a pain in the butt to convert WAV
downloads to FLAC and then add meta data automatically. This is silly, because
they're basically saying that they'll offer you the information for aesthetic
purposes, but will hide it from you if you try to do anything useful with it.

The tool requires that .wav files have the filenames as originally downloaded
from Beatport.
"""

import os
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import re
import urllib

__all__ = ["SillyBeatportScraper"]


class SillyBeatportScraper(object):
	def __init__(self):
		# regex used to extract important details from file name
		self.RE_EXTRACT = re.compile(r"([0-9]+)_([A-Za-z_]+?)\.wav")
		
		# used to build a URL to find the track info
		self.URL_PREFIX = "http://www.beatport.com"
	
	def meta_from_filename(self, filename):
		meta = {}
	
		print("debug: filename: {}".format(filename))
	
		track_info = self.RE_EXTRACT.match(filename)
		
		track_id = track_info.group(1)
		track_name = track_info.group(2).lower().replace("_", "-")
		
		page_url = self.URL_PREFIX + "/track/" + track_name + "/" + track_id
		
		page_data = urllib.urlopen(page_url).read()
		
		soup = BeautifulSoup(str(page_data))
		
		meta['track_title'] = "{} {}".format(
			soup.h2.contents[0], soup.h2.span.contents[0]
		) 
		meta['track_artists'] = [c.contents[0] for c in soup.find(
			'span', {'class': 'artists-value h4 fontCondensed'}
		).findAll('a')]
		meta['track_artists'].sort()
		
		meta['bpm'] = int(soup.find(text="BPM").findNext('span').contents[0])
		
		meta['genre'] = soup.find(text="Genre").findNext('span').a.contents[0]
		
		meta['labels'] = soup.find(
			'span', {'class': 'meta-label-value'}
		).a.contents[0]
		
		meta['release_name'] = soup.find(
			text="Releases"
		).findNext('span').a.contents[0]
		
		meta['release_info_url'] = self.URL_PREFIX + soup.find(
			text="Releases"
		).findNext('span').a['href']
		
		# TODO
		#meta['track_number'] = None
		#meta['catalog_number'] = None
		#meta['release_date'] = None
		
		#print(soup.find('span', {'class': 'artists-value h4 fontCondensed'}))
		
		# turn lists into comma separated strings
		meta = {
			key: str(", ".join(value)) if isinstance(value, list)
			                           else value
									   for key, value in meta.items()
		}
		
		# get rid of escape characters
		meta = {
			key: BeautifulSoup(
				value, convertEntities=BeautifulSoup.XML_ENTITIES
			).getText() if not isinstance(value, int) 
			            else value for key, value in meta.items()}
		
		return meta