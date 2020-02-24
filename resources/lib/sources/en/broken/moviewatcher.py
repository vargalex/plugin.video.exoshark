# -*- coding: utf-8 -*-

'''
    ExoShark Add-on

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

import re, urllib, urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['moviewatcher.is']
        self.base_link = 'https://moviewatcher.is'
        self.search_link = '/search?query=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:    
            t = cleantitle.getsearch(title)
            query = urlparse.urljoin(self.base_link, self.search_link % t.replace(' ', '+'))
            r = client.request(query)

            result = client.parseDOM(r, 'div', attrs={'class': 'one_movie-item'})
            result = [(client.parseDOM(i, 'div', attrs={'class': 'movie-titles'})[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            result = [(re.search('href="[^"]+(\d{4})"', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]
            if not len(result) == 1: raise Exception()

            try:
                qual = client.parseDOM(result, 'span', attrs={'class': 'qual'})[0]
            except:
                qual = 'SD'

            url = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, url)

            return (url, qual)
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url[0] == None: return sources

            r = client.request(url[0])

            qual = url[1].lower()
            if 'telesync' in qual or 'camrip' in qual: quality = 'CAM'
            else: quality = 'SD'

            items = re.findall('\'([^\']+redirect[^\']+)\'.+?server\:\s*([^<>]+)<', r)

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in items:
                try: 
                    host = item[1]
                    host = host.replace('www.', '').split('.', 1)[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    url = urlparse.urljoin(self.base_link, item[0])
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': '', 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        r = client.request(url, output='geturl')
        return r
