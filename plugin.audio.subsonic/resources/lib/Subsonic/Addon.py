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

import cgi
import logging
import sys
import urllib
import xbmcaddon, xbmcgui, xbmcplugin

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
                            'id': item_id})
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
    listitem = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem, 
                                isFolder=True, totalItems=total_items)

def add_artist(artist, total_items=0):
    url_queries = {'mode': 'get_music_directory', 'id': artist['id']}
    add_directory(url_queries, artist['name'], total_items=total_items) 

def add_song(song, img='', total_items=0):
    infolabels = {'title': song.get('title', get_string(30003)),
                  'artist': song.get('artist', get_string(30004)),
                  'album': song.get('album', get_string(30005)),
                  'tracknumber': song.get('track', 0),
                  'genre': song.get('genre', ''),
                  'duration': song.get('duration', 0),
                  }
    year = song.get('year', None)
    if year:
        infolabels['year'] = year
    add_music_item(song['id'], infolabels, img, total_items)

def add_album(album, img='', total_items=0):
    infolabels = {'title': album.get('title', get_string(30003)),
                  'artist': album.get('artist', get_string(30004)),
                  }
    add_directory({'mode': 'get_music_directory', 'id': album['id']}, 
                  album['title'], img, total_items)

def resolve_url(stream_url):
    xbmcplugin.setResolvedUrl(plugin_handle, True, 
                              xbmcgui.ListItem(path=stream_url))

def end_of_directory():
    xbmcplugin.endOfDirectory(plugin_handle)

def build_query(queries):
    return '&'.join([k+'='+urllib.quote(str(v)) for (k,v) in queries.items()])
                                
def build_plugin_url(queries):
    url = plugin_url + '?' + build_query(queries)
    return url

def parse_query(query):
    queries = cgi.parse_qs(query)
    q = {}
    for key, value in queries.items():
        q[key] = value[0]
    q['mode'] = q.get('mode', 'main')
    return q

def show_settings():
    addon.openSettings()

addon = xbmcaddon.Addon(id='plugin.video.subsonic')

