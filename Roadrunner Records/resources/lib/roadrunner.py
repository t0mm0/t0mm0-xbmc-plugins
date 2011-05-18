'''
    Roadrunner Records XBMC Plugin
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
import re
import urllib, urllib2
        
class Roadrunner:
    __BASE_URL = 'http://www.roadrunnerrecords.com'

    def __init__(self):
        pass

    def list_media(self, mode, sort, page=1, aux=''):
        html = self._get_html('%s/content.aspx' % mode, 
                               {'refID': '%s_content' % sort,
                                'key': sort,
                                'pagenum': page,
                                'pagesize': 4,
                                'aux': aux})
        return self._parse_page(html)

    def search(self, mode, query):
        html = self._get_html('search/index.aspx', {'mode': mode, 'q': query})
        return self._parse_page(html)    
        
    def resolve_stream(self, mode, song_id):
        resolved = False
        if mode == 'music':
            mode = 'audio'
        xml = self._get_html('widgets/%splayer_xml/%d' % (mode, song_id))
        s = re.search('src="(.+?)"', xml)
        if s:
            resolved = 'http://' + urllib.quote(Addon.unescape(s.group(1)))[7:]
        return resolved

    def _parse_page(self, html):
        r = '\d+"><img src="(.+?)".+?songID=(\d+)">(.+?)<\/a>' + \
                '.+?Artist.+?<a.+?>(.+?)<\/a>'
        songs = []
        for s in re.finditer(r, html, re.DOTALL):
            thumb, song_id, title, artist = s.groups()
            songs.append({'song_id': int(song_id),
                          'title': title,
                          'artist': artist,
                          'thumb': self.__BASE_URL + thumb})
        return songs

    def _build_url(self, path, queries={}):
        query = Addon.build_query(queries)
        return '%s/%s?%s' % (self.__BASE_URL, path, query) 

    def _fetch(self, url, form_data=False):
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
        
    def _get_html(self, path, queries={}):
        html = False
        url = self._build_url(path, queries)

        response = self._fetch(url)
        if response:
            html = response.read()
        else:
            html = False
        
        return html

