# -*- coding: UTF-8 -*-

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

import urllib, urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['coolmoviezone.info']
        self.base_link = 'http://coolmoviezone.info'
        self.search_link = '/index.php?s=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(title))
            r = client.request(query)

            result = client.parseDOM(r, 'div', attrs={'class': 'postarea'})[0]
            result = client.parseDOM(result, 'h1')
            if len(result) == 0: raise Exception()

            result = [(client.parseDOM(i, 'a')[0], client.parseDOM(i, 'a', ret = 'href')[0]) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].split('(%s' % year, 1)[0].strip().encode('utf-8')) and year in i[0]]
            if not len(result) == 1: raise Exception()

            return result[0]
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = client.request(url)

            items = client.parseDOM(r, 'table', attrs={'class': 'source-links'})[0]
            items = client.parseDOM(items, 'a', ret='href')

            for item in items:
                try:
                    if '1080p' in item: quality = '1080p'
                    elif '720p' in item: quality = '720p'
                    else: quality = 'SD'
                    valid, hoster = source_utils.is_host_valid(item, hostDict)
                    urls, host, direct = source_utils.check_directstreams(item, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url
