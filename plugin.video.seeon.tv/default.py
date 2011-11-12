'''
    azwatch.tv XBMC Plugin
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

import xbmc, xbmcplugin, xbmcgui
import urllib, urllib2, cgi
import re

BASE_URL = 'http://azwatch.tv/channels/?p='
def add_directory(url_queries, title, img='', total_items=0):
    url = build_plugin_url(url_queries)
    xbmc.log('adding dir: %s - %s' % (title, url))
    listitem = xbmcgui.ListItem(decode(title), iconImage=img, thumbnailImage=img)
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem, 
                                isFolder=True, totalItems=total_items)

def add_video_item(item_id, infolabels, img='', total_items=0):
    infolabels = decode_dict(infolabels)
    url = build_plugin_url({'mode': 'play',
                            'id': item_id})
    xbmc.log('adding item: %s - %s' % (infolabels['title'], url))
    listitem = xbmcgui.ListItem(infolabels['title'], iconImage=img, 
                                thumbnailImage=img)
    listitem.setInfo('video', infolabels)
    listitem.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem, 
                                isFolder=False, totalItems=total_items)

def build_plugin_url(queries):
    url = plugin_url + '?' + build_query(queries)
    return url

def build_query(queries):
    return '&'.join([k+'='+urllib.quote(str(v)) for (k,v) in queries.items()])
                                
def get_rtmp_url(page_url):
    response = urllib2.urlopen(page_url)
    html = response.read()
    swf_url, play = re.search('data="(.+?)".+?file=(.+?)\.flv', html, re.DOTALL).group(1, 2)
    rtmp = 'rtmp://68.68.30.239/edge'
    rtmp += '/%s swfUrl=%s pageUrl=%s tcUrl=%s' % (play, swf_url, page_url, rtmp)
    xbmc.log('stream: ' + rtmp)
    return rtmp

def parse_query(query):
    queries = cgi.parse_qs(query)
    q = {}
    for key, value in queries.items():
        q[key] = value[0]
    q['mode'] = q.get('mode', 'main')
    return q

def resolve_url(stream_url):
    xbmcplugin.setResolvedUrl(plugin_handle, True, 
                              xbmcgui.ListItem(path=stream_url))

#http://stackoverflow.com/questions/1208916/decoding-html-entities-with-python/1208931#1208931
def _callback(matches):
    id = matches.group(1)
    try:
        return unichr(int(id))
    except:
        return id

def decode(data):
    return re.sub("&#(\d+)(;|(?=\s))", _callback, data)

def decode_dict(data):
    for k, v in data.items():
        if type(v) is str or type(v) is unicode:
            data[k] = decode(v)
    return data

plugin_url = sys.argv[0]
plugin_handle = int(sys.argv[1])
plugin_query = plugin_queries = parse_query(sys.argv[2][1:])

if plugin_query['mode'] == 'play':
    stream = get_rtmp_url(plugin_query['id'])
    resolve_url(stream)
else:
    page = plugin_query.get('page', '1')
    response = urllib2.urlopen(BASE_URL + page)
    html = response.read()
    for channel in re.finditer('<td width="25%".+?src="(.*?)".+?alt="(.*?)".+?href="(.*?)"',
                    html):
        img, title, url = channel.group(1, 2, 3)
        add_video_item(url, {'title': title}, img)
    next_page = str(int(page) + 1)
    if re.search('Page:.+?%s<\/a' % (next_page), html):
        add_directory({'page': next_page}, 'Next Page')         
    xbmcplugin.endOfDirectory(plugin_handle)

