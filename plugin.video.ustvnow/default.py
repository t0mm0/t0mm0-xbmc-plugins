'''
    ustvnow XBMC Plugin
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

from resources.lib import Addon, ustvnow 
import sys
import xbmc, xbmcgui, xbmcplugin

Addon.plugin_url = sys.argv[0]
Addon.plugin_handle = int(sys.argv[1])
Addon.plugin_queries = Addon.parse_query(sys.argv[2][1:])

email = Addon.get_setting('email')
password = Addon.get_setting('password')
cookie_file = xbmc.translatePath('special://temp/ustvnow.cookies')
ustv = ustvnow.Ustvnow(email, password, cookie_file)

Addon.log('plugin url: ' + Addon.plugin_url)
Addon.log('plugin queries: ' + str(Addon.plugin_queries))
Addon.log('plugin handle: ' + str(Addon.plugin_handle))

mode = Addon.plugin_queries['mode']
play = Addon.plugin_queries['play']

if play:
    Addon.log('play ' + play)
    stream_type = ['rtmp', 'rtsp'][int(Addon.get_setting('stream_type'))]
    q = Addon.parse_query(play,False)
    stream_url = ustv.resolve_stream(q['server'], 
                                     q['app'], 
                                     q['stream'],
                                     quality=int(Addon.get_setting('quality')),
                                     stream_type=stream_type)
    xbmcplugin.setResolvedUrl(Addon.plugin_handle, True, 
                              xbmcgui.ListItem(path=stream_url))
    
elif mode == 'main':
    Addon.log(mode)
    Addon.add_directory({'mode': 'live'}, Addon.get_string(30001))
    Addon.add_directory({'mode': 'recordings'}, Addon.get_string(30002))

elif mode == 'live':
    Addon.log(mode)
    channels = ustv.get_channels()
    for c in channels:
        url = Addon.build_query({'server': c['server'],
                                'app': c['app'],
                                'stream': c['stream']})
        Addon.add_video_item(url,
                             {'title': '%s - %s: %s' % (c['name'], 
                                                        c['now']['time'], 
                                                        c['now']['title']),
                              'plot': c['now']['plot'],
                             },
                             img=c['icon'])

elif mode == 'recordings':
    Addon.log(mode)
    stream_type = ['rtmp', 'rtsp'][int(Addon.get_setting('stream_type'))]
    recordings = ustv.get_recordings(int(Addon.get_setting('quality')), 
                                     stream_type)
    for r in recordings:
        title = '%s (%s: %s)' % (r['title'], r['channel'], r['rec_date'])
        plot = '%s\n\nChannel: %s\nRecorded: %s\nduration: %s\nexpires: %s' % \
               (r['plot'], r['channel'], r['rec_date'], r['duration'], 
                r['expires'])
        Addon.add_video_item(r['stream_url'], {'title': title, 'plot': plot})
    
Addon.end_of_directory()
        

