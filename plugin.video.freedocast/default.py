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
    Addon.log('play ' + play)
    stream_url = freedo.resolve_stream(play)
    xbmcplugin.setResolvedUrl(Addon.plugin_handle, True, 
                              xbmcgui.ListItem(path=stream_url))
    
elif mode == 'main':
    Addon.log(mode)
    
Addon.end_of_directory()
        

