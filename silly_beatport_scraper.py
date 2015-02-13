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
        self.RE_EXTRACT = re.compile(r"([0-9]+)_([A-Za-z0-9_]+?)\.wav")
        
        # used to build a URL to find the track info
        self.URL_PREFIX = "http://pro.beatport.com"
    
    def album_info_from_url(self, album_info_url):
        meta = {}
        
        page_data = urllib.urlopen(album_info_url).read()
        
        soup = BeautifulSoup(str(page_data))
        
        meta['release_name'] = soup.find(
            text="Release"
        ).findNext('h1').contents[0]
        
        meta['track_listing'] = [
            {
                'track_number':
                    int(x.find('div', {'class': 'buk-track-num'}).contents[0]),
                'track_title':
                    x.find('div', {'class': 'buk-track-meta-parent'}).p.a.find('span', {'class': 'buk-track-primary-title'}).contents[0] + " (" +
                    x.find('div', {'class': 'buk-track-meta-parent'}).p.a.find('span', {'class': 'buk-track-remixed'}).contents[0] + ")"
            } for x in
            soup.h2.findNextSiblings('ul')[-1].findAll('li')
        ]
        
        meta['album_info_parse'] = soup.find('ul', {'class': 'interior-release-chart-content-list'})
        meta['album_info'] = {}
        for li in meta['album_info_parse'].findAll('li'):
            try:
                label = li.find('span', {'class': 'category'}).contents[0]
            except AttributeError:
                continue
            
            value = None
            try:
                value = li.find('span', {'class': 'value'}).contents[0]
            except TypeError:
                pass # no longer used
            
            if label == 'Release Date':
                date_particles = value.split('-')
                
                meta['album_info']['release-date'] = {}
                
                meta['album_info']['release-date']['year'] = int(date_particles[0])
                meta['album_info']['release-date']['month'] = int(date_particles[1])
                meta['album_info']['release-date']['day'] = int(date_particles[2])
            elif label == 'Catalog':
                meta['album_info']['catalogue-number'] = value
            
        del meta['album_info_parse']
        
        the_div = soup.find('div', {'class': 'interior-release-chart-artwork-parent'})
        the_image = the_div.find('img')['src']
        
        meta['album_art_url'] = the_image
        
        return meta
    
    def meta_from_filename(self, filename):
        meta = {}
    
        track_info = self.RE_EXTRACT.match(filename)
        
        track_id = track_info.group(1)
        track_name = track_info.group(2).lower().replace("_", "-")
        
        page_url = self.URL_PREFIX + "/track/" + track_name + "/" + track_id
        
        print(page_url)
        
        page_data = urllib.urlopen(page_url).read()
        
        soup = BeautifulSoup(str(page_data))
        
        meta['track_title'] = "{} ({})".format(
            soup.h1.contents[0].strip(), soup.h1.span.contents[0]
        ) 
        meta['track_artists'] = [c.contents[0] for c in soup.find(
            'span', {'class': 'value'}
        ).findAll('a')]
        meta['track_artists'].sort()
        
        meta['bpm'] = int(soup.find(text="BPM").findNext('span').contents[0])
        
        meta['genre'] = soup.find(text="Genre").findNext('span').a.contents[0]
        
        meta['labels'] = soup.find(
            'li', {'class': 'interior-track-content-item interior-track-labels'}
        ).find('span', {'class': 'value'}).a.contents[0]
        
        meta['release_info_url'] = self.URL_PREFIX + soup.find(
            text="Releases"
        ).findNext('a')['href']
        
        meta.update(self.album_info_from_url(meta['release_info_url']))
        
        # TODO
        #meta['track_number'] = None
        #meta['catalog_number'] = None
        #meta['release_date'] = None
        
        #print(soup.find('span', {'class': 'artists-value h4 fontCondensed'}))
        
        # turn lists into comma separated strings
        meta['track_artists'] = ", ".join(meta['track_artists'])
        
        # get rid of escape characters
        
        for k,v in meta.items():
            if not isinstance(v, (list, dict, int)):
                try:
                    meta[k] = BeautifulSoup(
                        v, convertEntities=BeautifulSoup.XML_ENTITIES
                    ).getText()
                except:
                    pass
        #meta = {
            #key: BeautifulSoup(
            #    value, convertEntities=BeautifulSoup.XML_ENTITIES
            #).getText() if not isinstance(value, int) 
            #            else value for key, value in meta.items()}
        
        for track in meta['track_listing']:
            if BeautifulSoup(track['track_title'], convertEntities=BeautifulSoup.XML_ENTITIES).getText() == meta['track_title']:
                meta['track_number'] = track['track_number']
                del meta['track_listing']
                break
        
        return meta
