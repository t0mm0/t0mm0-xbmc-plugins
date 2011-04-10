'''
    veetle.com XBMC Plugin
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
import simplejson as json
import urllib, urllib2

pluginUrl = sys.argv[0]
pluginHandle = int(sys.argv[1])
pluginQuery = sys.argv[2]

BASE_URL = 'http://www.veetle.com'
CHANNEL_LISTING = BASE_URL + '/channel-listing-cross-site.js'

def get_ajax_json(url):
    response = urllib2.urlopen(url)
    stream_json = json.loads(response.read())    
    if stream_json['success']:
        return stream_json['payload']
    else:
        print 'Problem getting info from: ' + url
        print 'Error returned: '+ stream_json['payload']
        return False

def get_stream_url(channel_id):
    return get_ajax_json(BASE_URL + '/index.php/channel/ajaxStreamLocation/' + channel_id + '/flash')

def get_channel_info(channel_id):
    try:
        return json.loads(get_ajax_json(BASE_URL + '/index.php/channel/ajaxInfo/' + channel_id))
    except ValueError, error_info:
        print 'Problem getting channel info: ' + channel_id
        print 'Error returned: ', error_info
        return {'title': 'unknown',
                'description': 'not available',
                'logo': {'sm': '', 'lg': ''}} 

if pluginQuery.startswith('?play='):
    #Play a stream with the given channel id
    channel_id = pluginQuery[6:]
    print 'veetle.com Channel ID: ' + channel_id
    stream_url = get_stream_url(channel_id)
    if stream_url:
        channel_info = get_channel_info(channel_id)            
        listitem = xbmcgui.ListItem(channel_info['title'], iconImage=channel_info['logo']['sm'], thumbnailImage=channel_info['logo']['sm'])
        infoLabels = {'plot': channel_info['description']}
        listitem.setInfo('video', infoLabels)
        xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(stream_url, listitem)    
else:
    #Load the channel list
    response = urllib2.urlopen(CHANNEL_LISTING)
    channels = json.loads(response.read())

    print 'Total veetle.com Channels: %d' % len(channels)

    #only list channels we can stream
    channels = [channel for channel in channels if channel.get('flashEnabled', False)]

    print 'Flash Enabled veetle.com Channels: %d' % len(channels)

    for channel in channels:
        url = pluginUrl + '?play=' + channel['channelId']
        sm = channel['logo'].get('sm', '')
        lg = channel['logo'].get('lg', '')
        if lg:
            thumb = lg
        else:
            thumb = sm
        
        listitem = xbmcgui.ListItem(channel['title'], iconImage=thumb, thumbnailImage=thumb)
        infoLabels = {'plot': channel['description']}
        listitem.setInfo('video', infoLabels)
        xbmcplugin.addDirectoryItem(pluginHandle, url, listitem, isFolder=False)
    xbmcplugin.endOfDirectory(pluginHandle)

