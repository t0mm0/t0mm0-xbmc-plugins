'''
    freedocast XBMC Plugin
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

from resources.lib import Addon, freedocast 
import sys
import xbmc, xbmcgui, xbmcplugin

Addon.plugin_url = sys.argv[0]
Addon.plugin_handle = int(sys.argv[1])
Addon.plugin_queries = Addon.parse_query(sys.argv[2][1:])

freedo = freedocast.Freedocast()

Addon.log('plugin url: ' + Addon.plugin_url)
Addon.log('plugin queries: ' + str(Addon.plugin_queries))
Addon.log('plugin handle: ' + str(Addon.plugin_handle))

mode = Addon.plugin_queries['mode']
play = Addon.plugin_queries['play']

if play:
    Addon.log('play: %s mode: %s' % (play, mode))    
    if mode == 'vid':
        stream_url = freedo.resolve_video(play)
    else:    
        stream_url = freedo.resolve_stream(play)
    Addon.resolve_url(stream_url)
    
elif mode == 'main':
    Addon.log(mode)
    Addon.add_directory({'mode': 'list_live'}, Addon.get_string(30000))
    Addon.add_directory({'mode': 'list_vid'}, Addon.get_string(30001))

elif mode == 'list_live':
    pn = int(Addon.plugin_queries.get('pn', 1))
    Addon.log('mode: %s page: %d' % (mode, pn))
    channels = freedo.get_channels(pn)
    for c in channels['channels']:
        Addon.add_video_item(c['id'], {'title': c['name']}, img=c['img'])
    if channels['more']:
        Addon.add_directory({'mode': 'list_live',
                             'pn': pn + 1}, Addon.get_string(30003))
        
elif mode == 'list_vid':
    pn = int(Addon.plugin_queries.get('pn', 1))
    Addon.log('mode: %s page: %d' % (mode, pn))
    videos = freedo.get_videos(pn)
    for v in videos['videos']:
        Addon.add_video_item(v['stream_url'], 
                             {'title': v['name']}, 
                             img=v['img'])
    if videos['more']:
        Addon.add_directory({'mode': 'list_vid',
                             'pn': pn + 1}, Addon.get_string(30003))
        
Addon.end_of_directory()
        

