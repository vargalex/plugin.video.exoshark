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

from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['www.timetowatch.video']
        self.base_link = 'https://www.timetowatch.video'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = cleantitle.normalize(title)
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(t)))
            r = self.scraper.get(query).content

            result = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'h2')[0], re.findall('>\s*(\d{4})\s*<', i)[0]) for i in result]

            url = [i[0] for i in result if cleantitle.get(i[1]) == cleantitle.get(title) and (year == i[2])][0]

            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            r = self.scraper.get(url).content

            items = client.parseDOM(r, 'form', attrs={'id': 'linkplayer.+?'})

            for item in items:
                try:
                    url = client.parseDOM(item, 'a', ret='href')[0]
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if valid:
                        url = client.replaceHTMLCodes(url)
                        url = url.encode('utf-8')
                        quality, info = source_utils.get_release_quality(url)
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url
