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

from resources.lib.Subsonic import Addon, Subsonic
import sys

Addon.plugin_url = sys.argv[0]
Addon.plugin_handle = int(sys.argv[1])
Addon.plugin_queries = Addon.parse_query(sys.argv[2][1:])

subsonic = Subsonic.Subsonic(Addon.get_setting('server'), 
                             Addon.get_setting('user'), 
                             Addon.get_setting('password'))

Addon.logging.debug('plugin queries: ' + str(Addon.plugin_queries))
Addon.logging.debug('plugin handle: ' + str(Addon.plugin_handle))

if subsonic.ping():
    if Addon.plugin_queries['mode'] == 'list_indexes': 
        subsonic.get_indexes(Addon.plugin_queries['folder_id'])
    elif Addon.plugin_queries['mode'] == 'list_playlists': 
        subsonic.get_playlists()
    elif Addon.plugin_queries['mode'] == 'playlist': 
        subsonic.get_playlist(Addon.plugin_queries['playlist_id'])
    elif Addon.plugin_queries['mode'] == 'get_music_directory': 
        subsonic.get_music_directory(Addon.plugin_queries['id'])
    elif Addon.plugin_queries['mode'] == 'play': 
        subsonic.play(Addon.plugin_queries['id'])
    elif Addon.plugin_queries['mode'] == 'search':
        search_mode = Addon.plugin_queries.get('search_mode', '')
        if search_mode: 
            q = Addon.plugin_queries.get('q', '')
            if not q:
                q = Addon.get_input(Addon.get_string({'artist': 30007,
                                                      'album': 30008,
                                                      'song': 30009}[search_mode]))
            if q:
                subsonic.search(search_mode, q)
        else:
            Addon.add_directory({'mode': 'search', 'search_mode': 'artist'}, 
                                Addon.get_string(30007))
            Addon.add_directory({'mode': 'search', 'search_mode': 'album'}, 
                                Addon.get_string(30008))
            Addon.add_directory({'mode': 'search', 'search_mode': 'song'}, 
                                Addon.get_string(30009))
            Addon.end_of_directory()
        
    else:
        Addon.add_directory({'mode': 'search'}, Addon.get_string(30006))
        Addon.add_directory({'mode': 'list_playlists'}, Addon.get_string(30011))
        subsonic.get_music_folders()
else:
    Addon.show_settings()

