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
import random
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
    
elif mode == 'browse':
    page = int(Addon.plugin_queries.get('page', 0))
    res_per_page = int(Addon.get_setting('res_per_page'))
    genre = Addon.plugin_queries.get('genre', '')
    sort = Addon.plugin_queries.get('sort', False)
    
    Addon.log('browse genre: %s, page: %d' % (genre, page))

    if genre:
        if not sort:
            sort = int(Addon.get_setting('sort'))
            if sort == 3:
                dialog = xbmcgui.Dialog()
                sort = dialog.select(Addon.get_string(30029),
                                     [Addon.get_string(30030),
                                      Addon.get_string(30031),
                                      Addon.get_string(30032)])
            sort = ['views', 'recent', 'alpha'][sort]
        videos = muzu.browse_videos(genre, sort, page, res_per_page)
        for v in videos:
            title = '%s: %s' % (v['artist'], v['title'])
            Addon.add_video_item(str(v['asset_id']),
                                 {'title': title,
                                  'plot': v['description'],
                                  'duration': str(v['duration']),
                                 },
                                 img=v['thumb'])
        Addon.add_directory({'mode': 'browse', 'genre': genre, 
                             'page': page + 1, 'sort': sort},
                            Addon.get_string(30026))
    else:
        Addon.add_directory({'mode': 'browse', 'genre': 'all'},
                            Addon.get_string(30028))    
        genres = muzu.get_genres()
        for g in genres:
            Addon.add_directory({'mode': 'browse', 'genre': g['id']}, g['name'])    

elif mode == 'jukebox':
    Addon.log(mode)
    mode = 'main'
    dialog = xbmcgui.Dialog()
    jam = dialog.select(Addon.get_string(30038), 
                        [Addon.get_string(30039), Addon.get_string(30040)])
    kb = xbmc.Keyboard('', Addon.get_string(30035), False)
    kb.doModal()
    if (kb.isConfirmed()):
        query = kb.getText()
        if query:
            country = Addon.get_setting('country')
            assets = muzu.jukebox(query, country)
            artist_id = assets['artist_ids'][0]
            if assets['artists']:
                q = dialog.select(Addon.get_string(30036), 
                                  assets['artists'])
                query = assets['artists'][q]
                artist_id = assets['artist_ids'][q]
                assets = muzu.jukebox(query, country)
            
            if jam:
                assets = muzu.jukebox(query, country, jam=artist_id)
            
            pl = Addon.get_new_playlist(xbmc.PLAYLIST_VIDEO)
            videos = assets.get('videos', False)        
            random.shuffle(videos)
            if videos:
                for v in videos:
                    title = '%s: %s' % (v['artist'], v['title'])
                    Addon.add_video_item(str(v['asset_id']),
                                         {'title': title,
                                         },
                                         img=v['thumb'],
                                         playlist=pl)  
                xbmc.Player().play(pl)   
            else:
                Addon.show_error([Addon.get_string(30037), query])

elif mode == 'search':
    Addon.log(mode)
    kb = xbmc.Keyboard('', Addon.get_string(30027), False)
    kb.doModal()
    if (kb.isConfirmed()):
        query = kb.getText()
        if query:
            videos = muzu.search(query)
            for v in videos:
                title = '%s: %s' % (v['artist'], v['title'])
                Addon.add_video_item(str(v['asset_id']),
                                     {'title': title,
                                      'plot': v['description'],
                                      'duration': str(v['duration']),
                                     },
                                     img=v['thumb'])
        else:
            mode = 'main'
    else:
        mode = 'main'

if mode == 'main':
    Addon.log(mode)
    Addon.add_directory({'mode': 'browse'}, Addon.get_string(30000))
    Addon.add_directory({'mode': 'jukebox'}, Addon.get_string(30034))
    Addon.add_directory({'mode': 'search'}, Addon.get_string(30027))

Addon.end_of_directory()
        

