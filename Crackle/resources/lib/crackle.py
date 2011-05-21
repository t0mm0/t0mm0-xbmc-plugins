'''
    Crackle XBMC Plugin
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

class Crackle:
    __BASE_URL = 'http://crackle.com'
    __BASE_VIDEO_URL = 'http://cdn1.crackle.com'
    __BASE_THUMB_URL = 'http://images2.crackle.com'
    __CATEGORIES = [{'name': Addon.get_string(30001), 'id': 46},
                    {'name': Addon.get_string(30002), 'id': 82},
                    {'name': Addon.get_string(30003), 'id': 114},
                    {'name': Addon.get_string(30004), 'id': 586},
                    ]
    __GENRES = [{'name': Addon.get_string(30005), 'id': ''},
                {'name': Addon.get_string(30006), 'id': 'action'},
                {'name': Addon.get_string(30007), 'id': 'comedy'},
                {'name': Addon.get_string(30008), 'id': 'crime'},
                {'name': Addon.get_string(30009), 'id': 'thriller'},
                {'name': Addon.get_string(30010), 'id': 'horror'},
                {'name': Addon.get_string(30011), 'id': 'sci-fi'},
                ]

    __TYPES = {'46': False,
               '82': [{'name': Addon.get_string(30012), 'id': 'a'},
                      {'name': Addon.get_string(30013), 'id': 'f'},
                      {'name': Addon.get_string(30015), 'id': 'c'},
                      ],
               '114': [{'name': Addon.get_string(30012), 'id': 'a'},
                       {'name': Addon.get_string(30013), 'id': 'f'},
                       {'name': Addon.get_string(30014), 'id': 'm'},
                       {'name': Addon.get_string(30015), 'id': 'c'},
                       ],
               '586': False,
               }        
    
    def __init__(self, proxy=''):
        self.proxy = proxy
        Addon.log('proxy: ' + proxy)

    def get_categories(self):
        return self.__CATEGORIES

    def get_genres(self):
        return self.__GENRES

    def get_types(self, cat_id):
        return self.__TYPES[cat_id]

    def get_channels(self, cat, genre, vtype, page=0):
        cl = Addon.build_query({'o': 1, 'fa': cat, 'fs': '', 'fx': '', 'fab': '', 'fg': genre, 'fry': ''})[1:]
        html = self.__get_html('chromewebapp/ShowList.aspx', {'cl': cl, 'p': page, 'fb': vtype}, use_proxy=True)
        if html.find('>&gt;</a>') > -1:
            more = True
        else:
            more = False
        channels = {'more': more, 'items': []}
        for channel in re.finditer('<li id="thumbImg".+?\'WatchShow\',(\d+?),(\d+?),.+?href, (\d+?)\).+?class="title">.+?(.+?)<\/.+?<\/li>', html, re.DOTALL):
            cid, pid, anid, title = channel.groups()
            m = title.find('height="18">')
            if m > -1:
                title = title[m + 12:]

            img = 'http://images2.crackle.com/profiles/channels/%s/BrowserPanelChannelBackground_300x169.jpg' % cid
                
            channels['items'].append({'title': title.strip(), 
                                      'cid': cid,
                                      'pid': pid,
                                      'id': anid,
                                      'img': img,
                                      })
        return channels
        

    def get_videos(self, cid, quality=360, page=0):
        html = self.__get_html('chromewebapp/MediaItemList.aspx', 
                               {'id': cid, 'p': page}, use_proxy=True)
        if html.find('id="pnlNextBtn"') > -1:
            more = True
        else:
            more = False
        videos = {'more': more, 'items': []}

        for video in re.finditer('<li class="(last)?".+?id="(\d+?)".+?src="(.+?)".+?showTitle">(.+?)&nbsp;<.+?<\/li>',
                                   html, re.DOTALL):
            media, url, title = video.group(2, 3, 4)
            path = '/'.join(url.split('/')[3:7])
            path = path[:path.find('tnb.jpg')]
            thumb = '%s/%stne.jpg' % (self.__BASE_THUMB_URL, path)
            video_url = '%s/%s%dp.mp4' % (self.__BASE_VIDEO_URL, path, int(quality))
            d = self.__get_html('chromewebapp/WatchShow.aspx', 
                                {'id': media}, use_proxy=True)

            title, rating, plot = re.search('"mediaTitle">(.+?)<\/h3>.*?Rating: (.+?)<\/b>.+?"mediaDesc">(.+?)<\/div>', d, re.DOTALL).groups()            
            
            cast = re.search('Cast:.+?synopsis">(.+?)<\/div>', d, re.DOTALL)
            if cast:
                cast = [c.strip() for c in cast.group(1).split(',')]
            else:
                cast = []
            director = re.search('Director:.+?synopsis">(.+?)<\/div>', d, re.DOTALL)
            if director:
                director = director.group(1)
            else:
                director = ''
                
            videos['items'].append({'title': title.strip(), 
                                    'thumb': thumb,
                                    'video_url': video_url,
                                    'mpaa': rating,
                                    'plot': plot,
                                    'cast': cast,
                                    'director': director,
                                    })
        return videos
        
    def resolve_movie(self, url, quality=360):
        html = self.__get_html(url, use_proxy=True)
        video_id = re.search('currentMediaID = (\d+)', html).group(1)
        xml = self.__get_html('app/VidDetails.ashx', {'flags': -1, 'id': video_id}, use_proxy=True)
        path = re.search(' p="(.+?)"', xml).group(1)
        video_url = '%s/%s%dp.mp4' % (self.__BASE_VIDEO_URL, path, int(quality))
        return video_url

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

