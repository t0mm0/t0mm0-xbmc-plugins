'''
    8tracks XBMC Plugin
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
import os.path
import re
import simplejson as json
import urllib, urllib2
import xbmc
        
class EightTracks:
    _BASE_URL = 'http://8tracks.com'
    _API_KEY = '04e89b30c1ae4f38e9f7a2fc3a6c55153ba7b98f'    
    SORT_RECENT = 'recent'
    SORT_HOT = 'hot'
    SORT_POPULAR = 'popular'
    SORT_RANDOM = 'random'
    
    def __init__(self):
        set_path = xbmc.translatePath(os.path.join(Addon.profile_path, 'set'))
        try:
            os.makedirs(os.path.dirname(set_path))
        except OSError:
            pass
            
        try:
            Addon.log('loading set number')
            f = open(set_path)
            self._set = f.readline().strip()    
            f.close()
        except IOError:
            Addon.log('getting set number')
            f = open(set_path, 'w')
            self._set = self.new_set()
            f.write(self._set)
            f.close()
    
    def new_set(self):
        return self._get_json('sets/new')['play_token']

    def mixes(self, sort='hot', tag='', search='', page=1):
        return self._get_json('mixes', {'sort': sort, 'tag': tag, 
                                        'q': search, 'page': page})

    def play(self, mix_id):
        return self._get_json('sets/%s/play' % self._set, {'mix_id': mix_id})

    def next(self, mix_id):
        return self._get_json('sets/%s/next' % self._set, {'mix_id': mix_id})

    def next_mix(self, mix_id):
        return self._get_json('sets/%s/next_mix' % self._set, 
                              {'mix_id': mix_id})

    def tags(self, page):
        return self._get_json('all/mixes/tags', {'tag_page': page})

    def _build_url(self, path, queries={}):
        query = Addon.build_query(queries)
        return '%s/%s?%s' % (self._BASE_URL, path, query) 

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

    def _get_json(self, method, queries={}):
        json_response = None
        queries['api_key'] = self._API_KEY
        url = self._build_url(method + '.json', queries)
        Addon.log('getting ' + url)
        try:
            response = urllib2.urlopen(url)
            try:
                json_response = json.loads(response.read())
            except ValueError:
                Addon.show_error([Addon.get_string(30005)])
                return False
        except urllib2.URLError, e:
            Addon.show_error([Addon.get_string(30006), str(e.reason)])
            return False

        if json_response.get('errors', None):              
            Addon.show_error(str(json_response['errors'][0]))  
            return False 
        else:
            return json_response
            
            
class EightTracksPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.et = kwargs['et']
        self.pl = Addon.get_playlist(xbmc.PLAYLIST_MUSIC, True)
        self.ended = False
        self.track_playing = False

    def onPlayBackStarted(self):
        Addon.log('onPlayBackStarted')
        self.add_next()
        
    def onPlayBackStopped(self):
        Addon.log('onPlayBackStopped')
        self.ended = True
        
    def play_mix(self, mix_id, mix_name, user, img):
        Addon.log('play_mix')
        self.mix_id = mix_id
        self.mix_name = mix_name
        self.user = user
        self.img = img
        self.add_next(True)
        self.play(self.pl)
        while not self.ended:
            Addon.log('player sleeping...')
            xbmc.sleep(1000)
        
    def add_next(self, first=False):
        Addon.log('add_next')
        if first:
            result = self.et.play(self.mix_id)
        else:
            result = self.et.next(self.mix_id)
        if result['set']['at_end']:
            Addon.log('moving to next mix')
            result = self.et.next_mix(self.mix_id)
            next_mix = result['next_mix']
            self.mix_id = next_mix['id']
            self.mix_name = next_mix['name']
            self.user = next_mix['user']['login']
            self.img = next_mix['cover_urls']['max200']
            result = self.et.play(self.mix_id)

        t = result['set']['track']
        comment = 'mix: %s by %s' % (self.mix_name, self.user)
        Addon.add_music_item(t['url'], {'title': t['name'], 
                                        'artist': t['performer'], 
                                        'comment': comment, 
                                        'album': t['release_name']},
                             img=self.img, playlist=self.pl)
        while not self.isPlaying() and not first and not self.ended:
            Addon.log('player sleeping (add_next)...')
            xbmc.sleep(1000)

