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

import re,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['vexmovies.org']
        self.base_link = 'http://vexmovies.org'
        self.search_link = '/advanced-search?%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urllib.urlencode({'search_query': title, 'orderby': '', 'order': '', 'tax_release-year[]': year, 'wpas': '1'})
            query = urlparse.urljoin(self.base_link, self.search_link % query)
            r = client.request(query)

            result = client.parseDOM(r, 'div', attrs={'class': 'datos'})
            if len(result) == 0: raise Exception()

            result = [(client.parseDOM(i, 'a')[0], client.parseDOM(i, 'a', ret = 'href')[0]) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].encode('utf-8'))]
            if not len(result) == 1: raise Exception()

            return result[0]
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            html = client.request(url)

            source = re.compile('<iframe src="(.+?)"',re.DOTALL).findall(html)[0]
            if 'consistent.stream' in source:
                html = client.request(source)
                page = re.compile('\:title="([^"]+)"').findall(html)[0]
                decode = client.replaceHTMLCodes(page)
                links = re.compile('"src":"([^"]+)',re.DOTALL).findall(decode)
                for link in links:
                    link = link.replace('\\','')
                    if '1080' in link:
                        quality='1080p'
                    elif '720' in link:
                        quality = '720p'
                    else:
                        quality = 'SD'
                    valid, hoster = source_utils.is_host_valid(link, hostDict)
                    urls, host, direct = source_utils.check_directstreams(link, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                    else:
                        sources.append({'source': 'CDN', 'quality': quality, 'language': 'en', 'url': link, 'direct': True, 'debridonly': False})
            return sources
        except:
            return sources

    def resolve(self, url):
        return url
