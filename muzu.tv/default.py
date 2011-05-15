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
import os.path
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
    if mode == 'playlist':
        Addon.log('playlist: %s' % play)
        videos = muzu.get_playlist(Addon.plugin_queries['network'], play) 
        if Addon.get_setting('random_pl') == 'true':
            random.shuffle(videos)
        pl = Addon.get_new_playlist(xbmc.PLAYLIST_VIDEO)
        res_dir = os.path.join(Addon.addon.getAddonInfo('path'), 
                               'resources')
        videos.insert(0, {'artist': 't0mm0', 
                          'title': 'muzu.tv',
                          'asset_id': 'file://%s/bodge.mp4' % res_dir,
                          'description': 'bodging auto playlist...',
                          'duration': 1,
                          'thumb': 'file://%s/bodge.png' % res_dir})
        for v in videos:
            title = '%s: %s' % (v['artist'], v['title'])
            Addon.add_video_item(str(v['asset_id']),
                                 {'title': title,
                                  'plot': v['description'],
                                  'duration': str(v['duration']),
                                 },
                                 img=v['thumb'],
                                 playlist=pl)  
        xbmc.Player().play(pl)
        mode = 'main'  
    else:
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
            if Addon.get_setting('hq') == 'true':
                hq = True
            else:
                hq = False
            videos = assets.get('videos', False)        
            random.shuffle(videos)
            res_dir = os.path.join(Addon.addon.getAddonInfo('path'), 
                                   'resources')
            videos.insert(0, {'artist': 't0mm0', 
                              'title': 'muzu.tv',
                              'asset_id': 'file://%s/bodge.mp4' % res_dir,
                              'description': 'bodging auto playlist...',
                              'duration': 1,
                              'thumb': 'file://%s/bodge.png' % res_dir})
            if videos:
                for v in videos:
                    title = unicode('%s: %s' % (v['artist'], v['title']), 'utf8')
                    Addon.add_video_item(str(v['asset_id']),
                                         {'title': title,
                                         },
                                         img=v['thumb'],
                                         playlist=pl)  
                xbmc.Player().play(pl)   
            else:
                Addon.show_error([Addon.get_string(30037), query])

elif mode == 'chart':
    Addon.log(mode)
    chart = Addon.plugin_queries.get('chart', '')    
    if chart:
        videos = muzu.get_chart(chart)
        for v in videos:
            title = unicode('%s (%s): %s' % 
                            (v['pos'], v['last_pos'], v['title']), 'utf8')
            Addon.add_video_item(str(v['asset_id']),
                                 {'title': title,},
                                 img=v['thumb'])
    else:
        Addon.add_directory({'mode': 'chart', 'chart': 1}, 
                            Addon.get_string(30042))
        Addon.add_directory({'mode': 'chart', 'chart': 2}, 
                            Addon.get_string(30043))
        Addon.add_directory({'mode': 'chart', 'chart': 3}, 
                            Addon.get_string(30044))
        Addon.add_directory({'mode': 'chart', 'chart': 4}, 
                            Addon.get_string(30045))
        Addon.add_directory({'mode': 'chart', 'chart': 5}, 
                            Addon.get_string(30046))

elif mode == 'list_playlists':
    Addon.log(mode)
    ob = Addon.plugin_queries.get('ob', False)
    if ob:
        country = Addon.get_setting('country')
        playlists = muzu.list_playlists(ob, country)
        for p in playlists:
            Addon.add_directory({'play': p['playlist_id'],
                                 'network': p['network_id'], 
                                 'mode': 'playlist'}, 
                                '%s (%s)' % (p['name'], p['network']))
    else:
        Addon.add_directory({'mode': 'list_playlists', 'ob': 'featured'}, 
                            Addon.get_string(30048))
        Addon.add_directory({'mode': 'list_playlists', 'ob': 'festivals'}, 
                            Addon.get_string(30049))
        Addon.add_directory({'mode': 'list_playlists', 'ob': 'views'}, 
                            Addon.get_string(30050))
        Addon.add_directory({'mode': 'list_playlists', 'ob': 'recent'}, 
                            Addon.get_string(30051))
        Addon.add_directory({'mode': 'channels'}, 
                            Addon.get_string(30052))

elif mode == 'channels':
    Addon.log(mode)

    network_id = Addon.plugin_queries.get('network_id', False)
    if network_id:
        playlists = muzu.list_playlists_by_network(network_id)
        for p in playlists:
            Addon.add_directory({'play': p['id'], 'network': network_id,
                                 'mode': 'playlist'},
                                p['name'], p['thumb'])
    else:
        page = int(Addon.plugin_queries.get('page', 0))
        res_per_page = 36
        genre = Addon.plugin_queries.get('genre', '')
        sort = Addon.plugin_queries.get('sort', False)
        country = Addon.get_setting('country')

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
            networks = muzu.browse_networks(genre, sort, page, country=country)
            for n in networks:
                title = '%s (%s videos)' % (n['title'], n['num_vids'])
                Addon.add_directory({'mode': 'channels', 
                                     'network_id': n['network_id']},
                                    title, 
                                    img=n['thumb'])
            Addon.add_directory({'mode': 'channels', 'genre': genre, 
                                 'page': page + 1, 'sort': sort},
                                Addon.get_string(30026))
        else:
            Addon.add_directory({'mode': 'channels', 'genre': 'all'},
                                Addon.get_string(30028))    
            genres = muzu.get_genres()
            for g in genres:
                Addon.add_directory({'mode': 'channels', 'genre': g['id']}, 
                                    g['name'])    

    
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
    Addon.add_directory({'mode': 'chart'}, Addon.get_string(30041))
    Addon.add_directory({'mode': 'list_playlists'}, Addon.get_string(30047))
    Addon.add_directory({'mode': 'search'}, Addon.get_string(30027))

Addon.end_of_directory()
      

