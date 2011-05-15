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
import xbmcgui

Addon.plugin_url = sys.argv[0]
Addon.plugin_handle = int(sys.argv[1])
Addon.plugin_queries = Addon.parse_query(sys.argv[2][1:])

subsonic = Subsonic.Subsonic(Addon.get_setting('server'), 
                             Addon.get_setting('user'), 
                             Addon.get_setting('password'))

Addon.log('plugin queries: ' + str(Addon.plugin_queries))
Addon.log('plugin handle: ' + str(Addon.plugin_handle))

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
    elif Addon.plugin_queries['mode'] == 'albums':
        page = Addon.plugin_queries.get('page', 0)
        sort = Addon.plugin_queries.get('sort', '')
        if sort:
            subsonic.get_album_list(sort, page)
        else:
            Addon.add_directory({'mode': 'albums', 'sort': 'random'}, 
                                Addon.get_string(30032))
            Addon.add_directory({'mode': 'albums', 'sort': 'newest'},
                                Addon.get_string(30033))
            Addon.add_directory({'mode': 'albums', 'sort': 'highest'}, 
                                Addon.get_string(30034))
            Addon.add_directory({'mode': 'albums', 'sort': 'frequent'}, 
                                Addon.get_string(30035))
            Addon.add_directory({'mode': 'albums', 'sort': 'recent'},
                                Addon.get_string(30036))
            Addon.end_of_directory()
    elif Addon.plugin_queries['mode'] == 'random':
        random_mode = Addon.plugin_queries.get('random_mode', False)
        if random_mode:
            queries = {}
            if Addon.plugin_queries.get('from_year'):
                queries['fromYear'] = Addon.plugin_queries.get('from_year')
            if Addon.plugin_queries.get('to_year'):
                queries['toYear'] = Addon.plugin_queries.get('to_year')
            if Addon.plugin_queries.get('genre'):
                queries['genre'] = Addon.plugin_queries.get('genre')
                
            dialog = xbmcgui.Dialog()
            if random_mode == 'custom':
                rnd = dialog.select(Addon.get_string(30013), 
                                    [Addon.get_string(30014),
                                     Addon.get_string(30015),
                                     Addon.get_string(30016),
                                     Addon.get_string(30017)])
                if rnd == 1 or rnd == 3:
                    queries['fromYear'] = dialog.numeric(0, 
                                                         Addon.get_string(30018), 
                                                         '2000')
                    queries['toYear'] = dialog.numeric(0, 
                                                       Addon.get_string(30019), 
                                                       queries['fromYear'])            
                if rnd >= 2:
                    queries['genre'] = Addon.get_input(Addon.get_string(30020))

            queries['size'] = dialog.numeric(0, Addon.get_string(30021), '10')            
            subsonic.get_random(queries)
        else:
            Addon.add_directory({'mode': 'random', 'random_mode': 'custom'}, 
                                 Addon.get_string(30022))
            Addon.add_directory({'mode': 'random', 'random_mode': 'preset', 
                                 'from_year': 1950, 'to_year': 1959}, 
                                Addon.get_string(30023))
            Addon.add_directory({'mode': 'random', 'random_mode': 'preset', 
                                 'from_year': 1960, 'to_year': 1969}, 
                                Addon.get_string(30024))
            Addon.add_directory({'mode': 'random', 'random_mode': 'preset', 
                                 'from_year': 1970, 'to_year': 1979}, 
                                Addon.get_string(30025))
            Addon.add_directory({'mode': 'random', 'random_mode': 'preset', 
                                 'from_year': 1980, 'to_year': 1989}, 
                                Addon.get_string(30026))
            Addon.add_directory({'mode': 'random', 'random_mode': 'preset', 
                                 'from_year': 1990, 'to_year': 1999}, 
                                Addon.get_string(30027))
            Addon.add_directory({'mode': 'random', 'random_mode': 'preset', 
                                 'from_year': 2000, 'to_year': 2009}, 
                                Addon.get_string(30028))
            Addon.add_directory({'mode': 'random', 'random_mode': 'preset', 
                                 'from_year': 2010, 'to_year': 2019}, 
                                Addon.get_string(30029))
            Addon.end_of_directory()


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
        subsonic.get_music_folders()
else:
    Addon.show_settings()

