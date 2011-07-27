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
import Addon
import cookielib
import os
import re
import urllib, urllib2

class Freedocast:
    __BASE_URL = 'http://freedocast.com'
    __BASE_IMAGE_URL = 'http://video3.letssync.com/lbvideos/'
    __BASE_VIDEO_URL = 'http://video3.letssync.com/lbvideos/'

    def __init__(self):
        pass
                    
    def get_categories(self):
        return None

    def get_genres(self):
        return None

    def get_types(self, cat_id):
        return None

    def get_channels(self, pn=1):
        channels = {'more': False, 'channels': []}
        list_page = self.__get_html('liveusers.aspx', queries={'pn': pn}, referer=self.__BASE_URL)
        for c in re.finditer('imgcont.+?href="(.+?)".+?src="(.+?)" alt="(.+?)"',
                             list_page, re.DOTALL):
            url, img, name = c.groups()
            channels['channels'].append({'id': url.split('/')[-1], 
                                         'img': img, 
                                         'name': name})
        if list_page.find('class=\'page_next\'') > -1:
            channels['more'] = True
        return channels

    def get_videos(self, pn=1):
        videos = {'more': False, 'videos': []}
        list_page = self.__get_html('videos.aspx', queries={'pn': pn})
        for v in re.finditer('lbvideos\/(.+?).jpg.+?target="_top">(.+?)<\/a>', 
                             list_page, re.DOTALL):
            v_id, name = v.groups()
            img = '%s/%s.jpg' % (self.__BASE_IMAGE_URL, v_id)
            stream_url = '%s/%s.flv' % (self.__BASE_VIDEO_URL, v_id)
            videos['videos'].append({'img': img, 
                                     'stream_url': stream_url, 
                                     'name': name})
        if list_page.find('class=\'page_next\'') > -1:
            videos['more'] = True
        return videos
        
    def resolve_stream(self, url):
        Addon.log('resolving stream: %s' % url)
        chan_page = self.__get_html(url)
        watch_url = re.search('id="player" src="(.+?)"', chan_page).group(1)
        watch_page = self.__get_html(watch_url, referer=self.__build_url(url))
        resolved = False
        s = re.search('file=(.+?)&streamer=(.+?)&', watch_page)
        if s:
            play, streamer = s.groups()
            app = '/'.join(streamer.split('/')[3:])
            resolved = '%s app=%s playpath=%s pageurl=%s' % \
                       (streamer, app, play, self.__build_url(watch_url))
            Addon.log('resolved to: %s' % resolved)
        else:
            s = re.search('stream: \'(rtmp.+?)\'', watch_page)
            if s:
                stream_url = s.group(1)
                resolved = '%s swfUrl=http://cdn.freedocast.com/player-octo/yume/v4/infinite-hd-player-FREEDOCAST.SWF pageUrl=%s' % (stream_url, watch_url)
            else:
                s = re.search('streamsUrl:  \'(.+?)\'', watch_page)
                if s:
                    xml_url = s.group(1)
                    xml = self.__get_html(xml_url)
                    s = re.search('<stream uri="(.+?)" stream="(.+?)"', xml)
                    if s:
                        tcurl, play = s.groups()
                        resolved = '%s/%s swfUrl=http://cdn.freedocast.com/player-octo/playerv2/swfs/broadkastplayer-yupp.swf pageUrl=%s' % (tcurl, play, watch_url)
        return resolved

    def resolve_video(self, v_id):
        Addon.log('resolving video: %s' % v_id)
        xml = self.__get_html('PlaylistXml.aspx', {'vid': v_id})
        s = re.search('url="(.+?)"', xml)
        if s:
            resolved = s.group(1)
            Addon.log('resolved to: %s' % resolved)
        else:
            resolved = False
        return resolved
        
    def __build_url(self, url, queries={}):
        if not url.startswith('http://'):
            url = '%s/%s' % (self.__BASE_URL, url)
        if queries:
            query = Addon.build_query(queries)
            url = url + '?' + query
        return url 

    def __fetch(self, url, form_data={}, headers=[]):
        opener = urllib2.build_opener()
        opener.addheaders = headers
        if form_data:
            Addon.log('posting: %s %s %s' % (url, str(form_data), str(headers)))
            req = urllib2.Request(url, form_data)
        else:
            Addon.log('getting: %s %s' % (url, str(headers)))
            req = url
        response = opener.open(req)
        try:
            response = opener.open(url)
            return response
        except urllib2.URLError, e:
            Addon.log(str(e), True)
            return False
        
    def __get_html(self, path, queries={}, referer=''):
        html = False
        headers = []
        url = self.__build_url(path, queries)
        if referer:
            headers.append(('referer', referer))

        response = self.__fetch(url, headers=headers)
        if response:
            html = response.read()
        else:
            html = False
        
        return html

