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

from resources.lib import Addon, muzutv 
import sys
import xbmc, xbmcgui, xbmcplugin

Addon.plugin_url = sys.argv[0]
Addon.plugin_handle = int(sys.argv[1])
Addon.plugin_queries = Addon.parse_query(sys.argv[2][1:])

email = Addon.get_setting('email')
password = Addon.get_setting('password')
muzu = muzutv.MuzuTv()

Addon.log('plugin url: ' + Addon.plugin_url)
Addon.log('plugin queries: ' + str(Addon.plugin_queries))
Addon.log('plugin handle: ' + str(Addon.plugin_handle))

mode = Addon.plugin_queries['mode']
play = Addon.plugin_queries['play']

if play:
    Addon.log('play: %s' % play)
    if Addon.get_setting('hq') == 'true':
        hq = True
    else:
        hq = False
    stream_url = muzu.resolve_stream(play, hq)
    Addon.resolve_url(stream_url)
    
elif mode == 'main':
    Addon.log(mode)
    Addon.add_directory({'mode': 'browse'}, Addon.get_string(30000))

elif mode == 'browse':
    page = int(Addon.plugin_queries.get('page', 0))
    res_per_page = int(Addon.get_setting('res_per_page'))
    genre = Addon.plugin_queries.get('genre', '')
    
    Addon.log('browse genre: %s, page: %d' % (genre, page))

    if genre:
        videos = muzu.browse_videos(genre, page, res_per_page)
        for v in videos:
            title = '%s: %s' % (v['artist'], v['title'])
            Addon.add_video_item(str(v['asset_id']),
                                 {'title': title,
                                  'plot': v['description'],
                                  'duration': str(v['duration']),
                                 },
                                 img=v['thumb'])
        Addon.add_directory({'mode': 'browse', 'genre': genre, 'page': page + 1},
                            Addon.get_string(30026))
    else:
        genres = muzu.get_genres()
        for g in genres:
            Addon.add_directory({'mode': 'browse', 'genre': g['id']}, g['name'])    

Addon.end_of_directory()
        

