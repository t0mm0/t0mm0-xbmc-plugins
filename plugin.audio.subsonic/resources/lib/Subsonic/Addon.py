'''
    Subsonic XBMC Plugin
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

import logging
import sys
import urllib
import xbmcaddon, xbmcgui, xbmcplugin

plugin_url = sys.argv[0]
plugin_handle = int(sys.argv[1])
plugin_query = sys.argv[2]
addon = xbmcaddon.Addon(id='plugin.video.subsonic')

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='Subsonic: %(levelname)s %(message)s',
    )

def show_error(details):
    error = ['', '', '']
    text = ''
    for k, v in enumerate(details):
        error[k] = v
        text += v + ' '
    logging.error(text)
    dialog = xbmcgui.Dialog()
    ok = dialog.ok(get_string(30000), error[0], error[1], error[2])
    
def get_setting(setting):
    return addon.getSetting(setting)
    
def get_string(string_id):
    return addon.getLocalizedString(string_id)   

def add_music_item(item_id, infolabels, img='', total_items=0):
    url = build_plugin_url({'mode': 'play',
                            'item_id': item_id})
    logging.debug('adding item: %s - %s' % (infolabels['title'], url))
    listitem = xbmcgui.ListItem(infolabels['title'], iconImage=img, 
                                thumbnailImage=img)
    listitem.setInfo('music', infolabels)
    listitem.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem, 
                                isFolder=False, totalItems=total_items)

def add_directory(url_queries, title, img='', total_items=0):
    url = build_plugin_url(url_queries)
    logging.debug('adding dir: %s - %s' % (title, url))
    print
    listitem = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem, 
                                isFolder=True, totalItems=total_items)

def end_of_directory():
    xbmcplugin.endOfDirectory(plugin_handle)

                                
def build_plugin_url(queries):
    url = plugin_url + '?' + '&'.join([k+'='+urllib.quote(str(v)) 
                                      for (k,v) in queries.items()])
    return url
    
def show_settings():
    addon.openSettings()

