'''
    jerryseinfeld.com XBMC Plugin
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

import re
import urllib2
import xbmcgui, xbmcplugin

plugin_handle = int(sys.argv[1])

def add_video_item(url, infolabels, img=''):
    listitem = xbmcgui.ListItem(infolabels['title'], iconImage=img, 
                                thumbnailImage=img)
    listitem.setInfo('video', infolabels)
    listitem.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem, isFolder=False)
                                

base_url = 'http://cdn.jerryseinfeld.com/assets'
html = urllib2.urlopen('http://www.jerryseinfeld.com/').read()
for v in re.finditer('"title":"(.+?)","filename":"(.+?)"' + 
                     ',"appearance":"(.+?)","venue":"(.+?)"', html):
    title, filename, year, venue = v.groups()
    add_video_item('%s/%s.mp4' % (base_url, filename), 
                   {'title': '%s (%s, %s)' % (title, venue, year), 
                    'year': int(year)},
                   '%s/%s.jpg' % (base_url, filename))

xbmcplugin.endOfDirectory(plugin_handle)      

