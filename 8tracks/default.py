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

from pprint import pprint

from resources.lib import Addon
from resources.lib.eighttracks import EightTracks, EightTracksPlayer 
import sys
import urllib
import xbmc, xbmcgui

Addon.plugin_url = sys.argv[0]
Addon.plugin_handle = int(sys.argv[1])
Addon.plugin_queries = Addon.parse_query(sys.argv[2][1:])

Addon.log('plugin url: ' + Addon.plugin_url)
Addon.log('plugin queries: ' + str(Addon.plugin_queries))
Addon.log('plugin handle: ' + str(Addon.plugin_handle))

et = EightTracks()

mode = Addon.plugin_queries['mode']
play = Addon.plugin_queries['play']
next = Addon.plugin_queries.get('next', None)

if play:
    user = Addon.plugin_queries['user']
    img = Addon.plugin_queries['img']
    mix_name = Addon.plugin_queries['mix_name']
    mix_id = play or next
    player = EightTracksPlayer(xbmc.PLAYER_CORE_DVDPLAYER, et=et)
    player.play_mix(mix_id, mix_name, user, img)
        
elif mode == 'mixes':
    sort = Addon.plugin_queries.get('sort', '')
    tag = Addon.plugin_queries.get('tag', '')
    search = Addon.plugin_queries.get('search', '')
    mytag = Addon.plugin_queries.get('mytag', '')
    page = int(Addon.plugin_queries.get('page', 1))
    if sort:
        result = et.mixes(sort, tag, search, page)
        mixes = result['mixes']
        for mix in mixes:
            name = '%s by %s (%s)' % (mix['name'], mix['user']['login'],
                                      mix['tag_list_cache'])
            Addon.add_directory({'play': mix['id'], 'mix_name': mix['name'], 
                                 'img': mix['cover_urls']['max200'],
                                 'user': mix['user']['login']}, 
                                name, mix['cover_urls']['max200'], folder=False)
        if result['next_page']:
            Addon.add_directory({'mode': 'mixes', 'sort': sort, 'tag': tag, 
                                 'search': search, 'page': result['next_page']}, 
                                Addon.get_string(30015))
    else:
        if search:
            kb = xbmc.Keyboard('', Addon.get_string(30017), False)
            kb.doModal()
            if (kb.isConfirmed()):
                search = kb.getText()
        if mytag:
            kb = xbmc.Keyboard('', Addon.get_string(30018), False)
            kb.doModal()
            if (kb.isConfirmed()):
                tag = kb.getText()
        
        Addon.add_directory({'mode': 'mixes', 'tag': tag, 'search': search, 
                             'sort': EightTracks.SORT_RECENT}, 
                            Addon.get_string(30011))
        Addon.add_directory({'mode': 'mixes', 'tag': tag, 'search': search,
                             'sort': EightTracks.SORT_HOT}, 
                            Addon.get_string(30012))
        Addon.add_directory({'mode': 'mixes', 'tag': tag, 'search': search,
                             'sort': EightTracks.SORT_POPULAR}, 
                            Addon.get_string(30013))

elif mode == 'tags':
    page = int(Addon.plugin_queries.get('page', 1))
    result = et.tags(page)
    Addon.add_directory({'mode': 'mixes', 'mytag': 1}, Addon.get_string(30018))
    for tag in result['tags']:
        Addon.add_directory({'mode': 'mixes', 'tag': tag['name']}, 
                            '%s (%d)' % (tag['name'], tag['taggings_count']))  
    Addon.add_directory({'mode': 'tags', 'page': page + 1}, 
                        Addon.get_string(30015))

elif mode == 'main':
    Addon.add_directory({'mode': 'mixes'}, Addon.get_string(30010))
    Addon.add_directory({'mode': 'tags'}, Addon.get_string(30016))
    Addon.add_directory({'mode': 'mixes', 'search': 1}, Addon.get_string(30017))

if not play:
    Addon.end_of_directory()
      

