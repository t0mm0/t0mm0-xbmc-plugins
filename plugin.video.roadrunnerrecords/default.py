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

from resources.lib import Addon, roadrunner 
import sys
import xbmc

Addon.plugin_url = sys.argv[0]
Addon.plugin_handle = int(sys.argv[1])
Addon.plugin_queries = Addon.parse_query(sys.argv[2][1:])

Addon.log('plugin url: ' + Addon.plugin_url)
Addon.log('plugin queries: ' + str(Addon.plugin_queries))
Addon.log('plugin handle: ' + str(Addon.plugin_handle))

rr = roadrunner.Roadrunner()

mode = Addon.plugin_queries['mode']
play = Addon.plugin_queries['play']

def display_songs(mode, songs):
    if mode == 'music':
        add = Addon.add_music_item
    else:
        add = Addon.add_video_item
    for s in songs:
        if mode == 'music':
            infolabels = {'title': s['title'], 
                          'artist': s['artist']}
        else:
            infolabels = {'title': '%s - %s' % 
                          (s['artist'], s['title'])}
        add(Addon.build_query({'mode': mode, 
                               'song_id': s['song_id']}),
            infolabels, img=s['thumb'], total_items=16)


if play:
    q = Addon.parse_query(play)
    stream_url = rr.resolve_stream(q['mode'], int(q['song_id']))
    Addon.resolve_url(stream_url)
    
elif mode == 'music' or mode == 'video':
    sort = Addon.plugin_queries.get('sort', False)
    page = int(Addon.plugin_queries.get('page', 1))
    aux = Addon.plugin_queries.get('aux', '')
    if sort == 'search':
        kb = xbmc.Keyboard('', Addon.get_string(30027), False)
        kb.doModal()
        if (kb.isConfirmed()):
            query = kb.getText()
            if query:
                display_songs(mode, rr.search(mode, query))
    elif sort:
        if (sort == 'most_played' or sort == 'least_played') and not aux:
            Addon.add_directory({'mode': mode, 'sort': sort, 'aux': 'week'}, 
                                Addon.get_string(30010))
            Addon.add_directory({'mode': mode, 'sort': sort, 'aux': 'month'}, 
                                Addon.get_string(30011))
            Addon.add_directory({'mode': mode, 'sort': sort, 'aux': 'year'}, 
                                Addon.get_string(30012))
            Addon.add_directory({'mode': mode, 'sort': sort, 'aux': 'all'}, 
                                Addon.get_string(30013))
        else:
            if aux == 'all':
                aux = ''        
            for x in range(4):
                songs = rr.list_media(mode, sort, page, aux)
                display_songs(mode, songs)
                page += 1
            Addon.add_directory({'mode': mode, 'sort': sort, 
                                 'page': page, 'aux': aux}, 
                                Addon.get_string(30009))
    else:
        Addon.add_directory({'mode': mode, 'sort': 'most_recent'}, 
                            Addon.get_string(30003))
        Addon.add_directory({'mode': mode, 'sort': 'most_played'}, 
                            Addon.get_string(30004))
        Addon.add_directory({'mode': mode, 'sort': 'least_played'}, 
                            Addon.get_string(30005))
        Addon.add_directory({'mode': mode, 'sort': 'highest_rated'}, 
                            Addon.get_string(30006))
        Addon.add_directory({'mode': mode, 'sort': 'most_commented'}, 
                            Addon.get_string(30007))
        Addon.add_directory({'mode': mode, 'sort': 'search'}, 
                            Addon.get_string(30008))
            
elif mode == 'main':
    Addon.add_directory({'mode': 'music'}, Addon.get_string(30001))
    Addon.add_directory({'mode': 'video'}, Addon.get_string(30002))

if not play:
    Addon.end_of_directory()
      

