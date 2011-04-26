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
import Addon
import re
import urllib2

class Ustvnow:
    __BASE_URL = 'http://ustvnow.com'
    __BASE_VIDEO_URL = 'ustvnow.com'
    __BASE_IMAGE_URL = 'http://lv2.ustvnow.com/ustvnow/images'
    __LOGOS = {'ABC': 'WHTM.png',
               'CBS': 'WHP.png',
               'CW': 'WLYH.png',
               'FOX': 'WPMT.png',
               'NBC': 'WGAL.png',
               'PBS': 'WITF.png',
               'AETV': 'AETV.png',
               'Animal Planet': 'APL.png',
               'Bravo': 'BRAVO.png',
               'Cartoon Network': 'TOON.png',
               'CNBC': 'CNBC.png',
               'CNN': 'CNN.png',
               'Comedy Central': 'COMEDY.png',
               'Discovery Channel': 'DSC.png',
               'ESPN': 'ESPN.png',
               'Food Network': 'FOOD.png',
               'FX': 'FX.png',
               'History': 'HISTORY.png',
               'Lifetime': 'LIFE.png',
               'Nickelodeon': 'NIK.png',
               'Syfy': 'SYFY.png',
               'TBS': 'TBS.png',
               'TNT': 'TNT.png',
               'USA': 'USA.png',
               }
    def __init__(self):
        self.proxy = ''
        pass
        
    def get_categories(self):
        return None

    def get_genres(self):
        return None

    def get_types(self, cat_id):
        return None

    def get_channels(self, quality):
        html = self.__get_html('callback.php', {'tab': 'showliveguide', 
                                                'subid': 7, 
                                                'layout': 'compact',
                                                'secid': '',
                                                'now': 'now'})
        channels = []
        for channel in re.finditer('class=\'chnl\'.+?playVideo\("(.+?)",.*?"(.+?)",.*?"(.+?)",.*?"(.+?)",.*?"(.+?)",.*?"(.+?)".+?title=\'(.+?)\'.+?class=\'play\'>(.+?)<\/a>(.+?)<\/div>',
                                   html, re.DOTALL):
            c = channel.groups()
            u = c[2].split(':')
            if u[0].find('.') > -1:
                url = 'rtmp://%s/%s/%s%d' % (u[0], u[1], c[1], 1)
            else:
                url = 'rtmp://%s.ustvnow.com/%s/%s%d' % (u[0], u[1], c[1], quality)
            now = {'time': c[6], 'title': c[7], 'plot': c[8]}
            icon = '%s/%s' % (self.__BASE_IMAGE_URL, self.__LOGOS.get(c[4], ''))    
            channels.append({'name': c[4], 'stream_url': url, 
                           'icon': icon, 'now': now})
        return channels
        

    def get_videos(self):
        return None
        
    def resolve_stream(self, channel, quality=350):
        return None

    def __build_url(self, path, queries={}):
        query = Addon.build_query(queries)
        return '%s/%s?%s' % (self.__BASE_URL, path, query) 

    def __get_html(self, path, queries={}, use_proxy=False):
        html = False
        url = self.__build_url(path, queries)

        if use_proxy and self.proxy:
            p = urllib2.ProxyHandler({'http': self.proxy})
            download = urllib2.build_opener(p).open
            Addon.log('getting with proxy: ' + url)
        else:
            download = urllib2.urlopen
            Addon.log('getting: ' + url)

        try:
            response = download(url)
            html = response.read()
            return html
        except urllib2.URLError, e:
            Addon.log(str(e), True)
            return False

