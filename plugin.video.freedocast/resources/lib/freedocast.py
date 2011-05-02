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

    def __init__(self):
        pass
                    
    def get_categories(self):
        return None

    def get_genres(self):
        return None

    def get_types(self, cat_id):
        return None

    def get_channels(self, quality):
        return None        

    def get_videos(self):
        return None
        
    def resolve_stream(self, url):
        Addon.log('resolving: %s' % url)
        chan_page = self.__get_html(url)
        watch_url = re.search('id="player" src="(.+?)"', chan_page).group(1)
        watch_page = self.__get_html(watch_url, referer=self.__build_url(url))
        play, streamer = re.search('file=(.+?)&streamer=(.+?)&', watch_page).groups()
        app = '/'.join(streamer.split('/')[3:])
        resolved = '%s app=%s playpath=%s pageurl=%s' % \
                   (streamer, app, play, self.__build_url(watch_url))
        Addon.log('resolved to: %s' % resolved)
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

