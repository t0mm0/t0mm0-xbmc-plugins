'''
    muzu.tv XBMC Plugin
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import Addon
import cookielib
import os
import re
import urllib, urllib2
from xml.etree import ElementTree as ET

class MuzuTv:
    __BASE_URL = 'http://www.muzu.tv'
    __API_KEY = 'a4Aais8F9J'
    __GENRES = [{'id': 'acoustic', 'name': Addon.get_string(30001)},
                {'id': 'alternative', 'name': Addon.get_string(30002)},
                {'id': 'blues', 'name': Addon.get_string(30003)},
                {'id': 'celtic', 'name': Addon.get_string(30004)},
                {'id': 'country', 'name': Addon.get_string(30005)},
                {'id': 'dance', 'name': Addon.get_string(30006)},
                {'id': 'electronic', 'name': Addon.get_string(30007)},
                {'id': 'emo', 'name': Addon.get_string(30008)},
                {'id': 'folk', 'name': Addon.get_string(30009)},
                {'id': 'gospel', 'name': Addon.get_string(30010)},
                {'id': 'hardcore', 'name': Addon.get_string(30011)},
                {'id': 'hiphop', 'name': Addon.get_string(30012)},
                {'id': 'indie', 'name': Addon.get_string(30013)},
                {'id': 'jazz', 'name': Addon.get_string(30014)},
                {'id': 'latin', 'name': Addon.get_string(30015)},
                {'id': 'metal', 'name': Addon.get_string(30016)},
                {'id': 'pop', 'name': Addon.get_string(30017)},
                {'id': 'poppunk', 'name': Addon.get_string(30018)},
                {'id': 'punk', 'name': Addon.get_string(30019)},
                {'id': 'reggae', 'name': Addon.get_string(30020)},
                {'id': 'rnb', 'name': Addon.get_string(30021)},
                {'id': 'rock', 'name': Addon.get_string(30022)},
                {'id': 'soul', 'name': Addon.get_string(30023)},
                {'id': 'world', 'name': Addon.get_string(30024)},
                {'id': 'other', 'name': Addon.get_string(30025)},                
                ]
    
    def __init__(self):
        pass
                            
    def get_genres(self):
        return self.__GENRES

    def get_types(self, cat_id):
        return None

    def browse_videos(self, genre, page, res_per_page, days=0):
        videos = []
        xml = self.__get_html('api/browse', {'muzuid': self.__API_KEY,
                                             'g': genre,
                                             'of': page * res_per_page,
                                             'l': res_per_page,
                                             'vd': days,
                                             })
        element = ET.fromstring(xml)
        for video in element.getiterator('video'):
            for img in video.find('thumbnails').getiterator('image'):
                if img.attrib['type'] =='6':
                    thumb = img.find('url').text
            videos.append({'duration': int(video.attrib['duration']),
                           'asset_id': int(video.attrib['id']),
                           'genre': video.attrib['genre'],
                           'title': video.findtext('title').strip(),
                           'artist': video.findtext('artistname').strip(),
                           'description': video.findtext('description').strip(),
                           'thumb': thumb.strip(),
                           })
        return videos
        
    def resolve_stream(self, asset_id, hq=True):
        resolved = False
        vt = 1
        if hq:
            vt = 2
        xml = self.__get_html('player/playAsset', {'assetId': asset_id,
                                                   'videoType': vt})
        s = re.search('src="(.+?)"', xml)
        if s:
            resolved = Addon.unescape(s.group(1))
        return resolved

    def __build_url(self, path, queries={}):
        query = Addon.build_query(queries)
        return '%s/%s?%s' % (self.__BASE_URL, path, query) 

    def __fetch(self, url, form_data=False):
        if form_data:
            Addon.log('posting: %s %s' % (url, str(form_data)))
            req = urllib2.Request(url, form_data)
        else:
            Addon.log('getting: ' + url)
            req = url

        try:
            response = urllib2.urlopen(url)
            return response
        except urllib2.URLError, e:
            Addon.log(str(e), True)
            return False
        
    def __get_html(self, path, queries={}):
        html = False
        url = self.__build_url(path, queries)

        response = self.__fetch(url)
        if response:
            html = response.read()
        else:
            html = False
        
        return html

    def __login(self):
        Addon.log('logging in')
        policy = cookielib.DefaultCookiePolicy(rfc2965=True, strict_rfc2965_unverifiable=False)    
        self.cj = cookielib.MozillaCookieJar(self.cookie_file)
        self.cj.set_policy(policy)

        if os.access(self.cookie_file, os.F_OK):
            self.cj.load(ignore_discard=True)

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(opener)
        self.cj.clear_session_cookies()
        
        url = self.__build_url('cgi-bin/oc/manage.cgi')
        form_data = urllib.urlencode({'a': 'do_login', 
                                      'force_direct': '0',
                                      'manage_proper': '1',
                                      'input_username': self.user,
                                      'input_password': self.password
                                      })
        response = self.__fetch(self.__LOGIN_URL, form_data)
        self.cj.save(ignore_discard=True)

