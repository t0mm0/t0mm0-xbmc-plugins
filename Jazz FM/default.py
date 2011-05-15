'''
    jazzfm.com XBMC Plugin
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
from BeautifulSoup import BeautifulSoup
import urllib, urllib2, cgi
import re

pluginUrl = sys.argv[0]
pluginHandle = int(sys.argv[1])
pluginQuery = sys.argv[2]

BASE_URL = 'http://www.jazzfm.com'
RTMP_APP = 'rtmp://listen.onmyradio.net/JAZZFM' 
LIVE_APP = 'http://listen.onmyradio.net:8050/' 
#'rtmp://listen.onmyradio.net/shoutcast' #&file=jazzfm.stream

#http://stackoverflow.com/questions/1208916/decoding-html-entities-with-python/1208931#1208931
def _callback(matches):
    id = matches.group(1)
    try:
        return unichr(int(id))
    except:
        return id

def decode_unicode_references(data):
    return re.sub("&#(\d+)(;|(?=\s))", _callback, data)
    
def add_stream(title, thumb, comment, data_url):
    listitem = xbmcgui.ListItem(title, iconImage=thumb, thumbnailImage=thumb)
    infoLabels = {'title': title, 'artist': 'jazzfm.com', 'comment': comment}
    listitem.setInfo('music', infoLabels)
    url = pluginUrl + '?mode=play&data_url=' + data_url + '&thumb=' + thumb + '&title=' + title
    xbmcplugin.addDirectoryItem(pluginHandle, url, listitem, isFolder=False)


query = cgi.parse_qs(pluginQuery[1:])

for key, value in query.items():
    query[key] = value[0]
query['mode'] = query.get('mode', '')    
if query['mode'] == 'play':
    stream = pluginQuery[6:]
    listitem = xbmcgui.ListItem('test', iconImage=query['thumb'], thumbnailImage=query['thumb'])
    infoLabels = {'title': query['title'], 'artist': 'jazzfm.com'}
    listitem.setInfo('music', infoLabels)
    if query.get('data_url', False):
        listitem.setProperty('PlayPath', 'MP4:jazzfm_' + query['data_url'] + '.m4a')
        app = RTMP_APP    
    else:
        #listitem.setProperty('PlayPath', 'jazzfm.stream')
        app = LIVE_APP            
    xbmc.Player().play(app, listitem)
  
else:
    response = urllib2.urlopen(BASE_URL + '/listening')
    soup = BeautifulSoup(response.read())
    
    shows = soup.findAll('li', attrs={'class': 'group'})

    live_show = soup.find('ul', attrs={'class': 'listen-live-panel'}).h2.string

    add_stream('Live Stream - ' + live_show, 'http://www.jazzfm.com/wp-content/themes/jazzfm/images/logo.jpg', 'Listen in Colour!', '')

    for show in shows:
        thumb = show.img['src']
        title = decode_unicode_references(show.h3.a.string)
        comment = decode_unicode_references(show.p.string)
        data_url = show.p.findNextSibling('p').a['data_url']
        add_stream(title, thumb, comment, data_url)
    xbmcplugin.endOfDirectory(pluginHandle)

