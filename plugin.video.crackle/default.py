'''
    Crackle XBMC Plugin
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

from resources.lib import Addon, crackle 
import sys
import xbmcgui, xbmcplugin

Addon.plugin_url = sys.argv[0]
Addon.plugin_handle = int(sys.argv[1])
Addon.plugin_queries = Addon.parse_query(sys.argv[2][1:])

proxy = ''
if Addon.get_setting('proxy') == 'true':
    proxy = Addon.get_setting('proxy_server')

crack = crackle.Crackle(proxy)

Addon.log('plugin url: ' + Addon.plugin_url)
Addon.log('plugin queries: ' + str(Addon.plugin_queries))
Addon.log('plugin handle: ' + str(Addon.plugin_handle))

mode = Addon.plugin_queries['mode']
play = Addon.plugin_queries['play']

if play:
    Addon.log('play ' + play)
    video_url = crack.resolve_movie(play)
    xbmcplugin.setResolvedUrl(Addon.plugin_handle, True, 
                              xbmcgui.ListItem(path=video_url))
    
if mode == 'main':
    Addon.log(mode)
    for cat in crack.get_categories():
        Addon.add_directory({'mode': 'list_genres', 'cat': cat['id']}, 
                            cat['name'])

if mode == 'list_genres':
    Addon.log('%s: cat=%s' % (mode, Addon.plugin_queries['cat']))
    for genre in crack.get_genres():
        Addon.add_directory({'mode': 'list_types', 
                             'cat': Addon.plugin_queries['cat'],
                             'genre': genre['id'],
                             }, 
                            genre['name'])

if mode == 'list_types':
    Addon.log('%s: cat=%s genre=%s' % (mode, Addon.plugin_queries['cat'],
                                       Addon.plugin_queries.get('genre', '')))
    types = crack.get_types(Addon.plugin_queries['cat'])
    if not types:
        Addon.plugin_queries['type'] = 'a'
        mode = 'list_channels'
    else:
        for t in types:
            Addon.add_directory({'mode': 'list_channels', 
                                 'cat': Addon.plugin_queries['cat'],
                                 'genre': Addon.plugin_queries.get('genre', ''),
                                 'type': t['id'],
                                 }, 
                                t['name'])
                            
if mode == 'list_channels':
    page = Addon.plugin_queries.get('page', 0)
    Addon.log('%s: cat=%s genre=%s type=%s page=%s' % (
                                       mode, Addon.plugin_queries['cat'],
                                       Addon.plugin_queries.get('genre', ''),
                                       Addon.plugin_queries.get('type', 'a'),
                                       page))
    channels = crack.get_channels(Addon.plugin_queries['cat'],
                                  Addon.plugin_queries.get('genre', ''),
                                  Addon.plugin_queries.get('type', 'a'),
                                  page=page)
    for c in channels['items']:
        Addon.add_directory({'mode': 'list_videos', 
                             'cid': c['cid'],
                             }, 
                            c['title'],
                            img=c['img'],
                            fanart=c['img'],
                            )

    if channels['more']:
        Addon.add_directory({'mode': 'list_channels', 
                             'cat': Addon.plugin_queries['cat'],
                             'genre': Addon.plugin_queries.get('genre', ''),
                             'type': Addon.plugin_queries.get('type', 'a'),
                             'page': int(page) + 1,
                             }, 
                            Addon.get_string(30000))

if mode == 'list_videos':
    page = Addon.plugin_queries.get('page', 0)
    Addon.log('%s: cid=%s page=%s' % (mode, Addon.plugin_queries['cid'], page))
    quality = ['360', '480'][int(Addon.get_setting('quality'))]
    videos = crack.get_videos(Addon.plugin_queries['cid'], quality=quality, page=page)

    for v in videos['items']:
        Addon.add_video_item(v['video_url'],
                             {'title': v['title'],
                              'plot': v['plot'], 
                              'cast': v['cast'],
                              'director': v['director'],
                              'mpaa': v['mpaa'],
                              }, 
                             img=v['thumb'],
                             fanart=v['thumb'])

    if videos['more']:
        Addon.add_directory({'mode': 'list_videos', 
                             'cid': Addon.plugin_queries['cid'],
                             'page': int(page) + 1,
                             }, 
                            Addon.get_string(30000))
    
Addon.end_of_directory()
        

