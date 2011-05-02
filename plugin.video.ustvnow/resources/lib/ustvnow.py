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
import cookielib
import os
import re
import urllib, urllib2

class Ustvnow:
    __BASE_URL = 'http://ustvnow.com'
    __BASE_VIDEO_URL = 'ustvnow.com'
    __BASE_DVR_URL = 'dvr1.ustvnow.com:1935/dvrrokuplay'
    __BASE_IMAGE_URL = 'http://lv2.ustvnow.com/ustvnow/images'
    __LOGIN_URL = __BASE_URL + '/cgi-bin/oc/manage.cgi'
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
    def __init__(self, user, password, cookie_file):
        self.user = user
        self.password = password
        self.cookie_file = cookie_file
                    
    def get_categories(self):
        return None

    def get_genres(self):
        return None

    def get_types(self, cat_id):
        return None

    def get_channels(self):
        html = self.__get_html('callback.php', {'tab': 'showliveguide', 
                                                'subid': 7, 
                                                'layout': 'compact',
                                                'secid': '',
                                                'now': 'now'})
        channels = []
        for channel in re.finditer('class=\'chnl\'.+?playVideo\("(.+?)",.*?"(.+?)",.*?"(.+?)",.*?"(.+?)",.*?"(.+?)",.*?"(.+?)".+?title=\'(.+?)\'.+?class=\'play\'>(.+?)<\/a>(.+?)<\/div>',
                                   html, re.DOTALL):
            c = channel.groups()
            server, app = c[2].split(':')
            now = {'time': c[6], 'title': c[7], 'plot': c[8]}
            icon = '%s/%s' % (self.__BASE_IMAGE_URL, self.__LOGOS.get(c[4], ''))    
            channels.append({'name': c[4], 'stream': c[1], 
                           'server': server, 'app': app, 
                           'icon': icon, 'now': now})
        return channels        

    def get_recordings(self, quality=1, stream_type='rtmp'):
        html = self.__get_html('callback.php', {'tab': 'showcustomerrecordings',
                                                'username': self.user,
                                                })
        recordings = []
        for r in re.finditer('<td class="center">(.+?)<\/td>.+?playVideo\(".+?","(.+?)".+?play\'>(.+?)<\/a><\/strong>(.+?)<\/td>.*?<td>(.+?)<\/td>.*?>(.+?)<\/td>.*?<td>(.+?)<\/td>.*?<\/tr>', html, re.DOTALL):
            chan, filename, title, plot, rec_date, duration, expires = r.groups()
            url = '%s://%s/%s_%s.mp4' % (stream_type,
                                       self.__BASE_DVR_URL,
                                       filename,
                                       ['350', '650', '950'][quality])
            recordings.append({'channel': chan,
                               'stream_url': url,
                               'title': title,
                               'plot': plot,
                               'rec_date': rec_date,
                               'duration': duration,
                               'expires': expires,
                               })
        return recordings
        
    def resolve_stream(self, server, app, channel, quality=1, stream_type='rtmp'):
        Addon.log('resolving stream: ' + channel)
        self.__login()
        stream_name = self.__get_html('getencstreamname.php', {'sname': channel})
        if server.find('.') > -1:
            url = '%s://%s:1935/%s/%s%d' % \
                        (stream_type, server, app, stream_name, int(quality) + 1)
        else:
            url = '%s://%s.ustvnow.com:1935/%s/%s%d' % \
                        (stream_type, server, app, stream_name, int(quality) + 1)
        Addon.log('resolved to: ' + url)
        return url

    def __build_url(self, path, queries={}):
        query = Addon.build_query(queries)
        return '%s/%s?%s' % (self.__BASE_URL, path, query) 

    def __fetch(self, url, form_data=False):
        if form_data:
            Addon.log('posting: %s %s' % (url, str(form_data)))
            req = urllib2.Request(url, form_data)
        else:
            Addon.log('getting: ' + url)
            req = url
        response = urllib2.urlopen(req)
        try:
            response = urllib2.urlopen(url)
            return response
        except urllib2.URLError, e:
            Addon.log(str(e), True)
            return False
        
    def __get_html(self, path, queries={}):
        html = False
        url = self.__build_url(path, queries)

        response = self.__fetch(url)
        if response:
            html = response.read()
        else:
            html = False
        
        return html

    def __login(self):
        Addon.log('logging in')
        policy = cookielib.DefaultCookiePolicy(rfc2965=True, strict_rfc2965_unverifiable=False)    
        self.cj = cookielib.MozillaCookieJar(self.cookie_file)
        self.cj.set_policy(policy)

        if os.access(self.cookie_file, os.F_OK):
            self.cj.load(ignore_discard=True)

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(opener)
        self.cj.clear_session_cookies()
        
        url = self.__build_url('cgi-bin/oc/manage.cgi')
        form_data = urllib.urlencode({'a': 'do_login', 
                                      'force_direct': '0',
                                      'manage_proper': '1',
                                      'input_username': self.user,
                                      'input_password': self.password
                                      })
        response = self.__fetch(self.__LOGIN_URL, form_data)
        self.cj.save(ignore_discard=True)

