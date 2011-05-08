'''
    Subsonic XBMC Plugin
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

import simplejson as json
import urllib, urllib2
import xbmc
import Addon

class Subsonic:
    bitrates = [32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]
    def __init__(self, server, user, password):
        self.server = server
        self.user = user
        self.password = password
        self.api_version = '1.4.0'
        self.client_name='xbmc'
        
    def ping(self):
        Addon.log('ping')
        payload = self.__get_json('ping.view')
        return payload
        
    def get_music_folders(self):
        Addon.log('get_music_folders')
        payload = self.__get_json('getMusicFolders.view')
        if payload:
            folders = self.listify(payload['musicFolders']['musicFolder'])
            total = len(folders)
            for folder in folders:
                if type(folder) is dict:
                    Addon.add_directory({'mode': 'list_indexes', 
                                         'folder_id': folder['id']}, 
                                        folder['name'], total_items=total)
            Addon.add_directory({'mode': 'albums'}, Addon.get_string(30031))
            Addon.add_directory({'mode': 'search'}, Addon.get_string(30006))
            Addon.add_directory({'mode': 'list_playlists'}, 
                                Addon.get_string(30011))
            Addon.add_directory({'mode': 'random'}, Addon.get_string(30012))
            Addon.end_of_directory()

    def get_indexes(self, folder_id):
        Addon.log('get_indexes: ' + folder_id)
        payload = self.__get_json('getIndexes.view', {'musicFolderId': folder_id})
        if payload:
            indexes = payload['indexes'].get('index', False)
            shortcuts = self.listify(payload['indexes'].get('shortcut', False))
            if indexes:
                index = []
                if shortcuts:
                    [Addon.add_artist(s) for s in shortcuts if type(s) is dict]
                [index.extend(i) for i in [self.listify(i['artist']) 
                    for i in self.listify(indexes)]]
                [Addon.add_artist(i) for i in index if type(i) is dict]
                Addon.end_of_directory()
            else:
                Addon.show_dialog([Addon.get_string(30030)])

    def get_music_directory(self, music_id):
        Addon.log('get_music_directory: ' + music_id)
        payload = self.__get_json('getMusicDirectory.view', {'id': music_id})
        if payload:
            songs = self.listify(payload['directory']['child'])
            self.display_music_directory(songs)

    def get_album_list(self, sort, page=0):
        Addon.log('get_album_list: ' + sort)
        payload = self.__get_json('getAlbumList.view', {'type': sort,
                                  'size': 50, 'offset': int(page) * 50})
        if payload:
            if payload['albumList']:
                albums = self.listify(payload['albumList']['album'])
                self.display_music_directory(albums, False)
                if len(albums) == 50:
                    Addon.add_directory({'mode': 'albums', 'sort': sort, 
                                         'page': int(page) + 1},
                                        Addon.get_string(30037))
        Addon.end_of_directory()
        
    def display_music_directory(self, songs, done=True):
        for song in songs: 
            if type(song) is dict:
                cover_art = self.get_cover_art_url(song.get('coverArt', None))
                if song['isDir']:
                    Addon.add_album(song, cover_art)
                else:    
                    Addon.add_song(song, cover_art)
        if done:
            Addon.end_of_directory()
    
    def get_playlists(self):
        Addon.log('get_playlists')
        payload = self.__get_json('getPlaylists.view')
        if payload:
            playlists = self.listify(payload['playlists']['playlist'])
            total = len(playlists)
            Addon.log('playlists: ' + str(playlists))
            for playlist in playlists:
                if type(playlist) is dict:
                    Addon.add_directory({'mode': 'playlist', 
                                         'playlist_id': playlist['id']}, 
                                        playlist['name'], 
                                        total_items=total)
            Addon.end_of_directory()

    def get_playlist(self, playlist_id):
        Addon.log('get_playlist: ' + playlist_id)
        payload = self.__get_json('getPlaylist.view', {'id': playlist_id})
        if payload:
            songs = self.listify(payload['playlist']['entry'])
            self.display_music_directory(songs)

    def get_random(self, queries):
        Addon.log('get_random: ' + str(queries))
        payload = self.__get_json('getRandomSongs.view', queries)
        if payload:
            if payload.get('randomSongs', False):
                songs = self.listify(payload['randomSongs']['song'])
                self.display_music_directory(songs)
            else:
                Addon.show_dialog([Addon.get_string(30010)])
            
    def play(self, song_id):
        Addon.log('play: ' + song_id)
        if Addon.get_setting('transcode') == 'true':
            bitrate = self.bitrates[int(Addon.get_setting('bitrate'))]
            Addon.resolve_url(self.build_rest_url('stream.view', 
                                                  {'id': song_id,
                                                   'maxBitRate': bitrate}))
        else:
            Addon.resolve_url(self.build_rest_url('download.view', 
                                                  {'id': song_id}))
    def search(self, search_mode, query): 
        Addon.log('search: ' + query)
        queries = {'query': query, 'albumCount': 0, 'artistCount': 0,
                   'songCount': 0}
        queries[search_mode + 'Count'] = 999
        payload = self.__get_json('search2.view', queries)        
        if payload:
            if payload['searchResult2']:
                items = self.listify(payload['searchResult2'][search_mode])
                if search_mode == 'artist':
                    [Addon.add_artist(i) for i in items if type(i) is dict]
                    Addon.end_of_directory()
                else:
                    self.display_music_directory(items)
            else:
                Addon.show_dialog([Addon.get_string(30010)])

    def get_cover_art_url(self, cover_art_id):
        url = ''
        if cover_art_id:
            url = self.build_rest_url('getCoverArt.view', {'id': cover_art_id})
            Addon.log('cover art: ' + url)
        return url
                      
    def build_rest_url(self, method, queries):
        queries.update({'v': self.api_version, 
                        'c': self.client_name, 
                        'u': self.user, 
                        'p': self.password,
                        'f': 'json'})
        Addon.log('queries: ' + str(queries))
        query = Addon.build_query(queries)
        return '%s/rest/%s?%s' % (self.server, method, query) 
    
    def listify(self, data):
        if type(data) is not list:
            return [data]
        else:
            return data

    def __get_json(self, method, queries={}):
        json_response = None
        url = self.build_rest_url(method, queries)
        Addon.log('getting ' + url)
        try:
            response = urllib2.urlopen(url)
            try:
                json_response = json.loads(response.read())
            except ValueError:
                Addon.show_error([Addon.get_string(30002)])
                return False
        except urllib2.URLError, e:
            Addon.show_error([Addon.get_string(30001), str(e.reason)])
            return False

        payload = json_response.get('subsonic-response', None)
        if payload.get('status', 'failed') == 'ok':              
            return payload
        else:
            Addon.show_error([payload['error']['message'], 
                       'json version: ' + payload['version']])  
            return False 

