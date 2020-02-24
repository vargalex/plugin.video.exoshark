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


import re, urllib, urlparse, traceback

from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import cfscrape
from resources.lib.modules import log_utils
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['hdm.to']
        self.base_link = 'https://hdm.to'
        self.search_link = '/search/%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['title']
            year = data['year']

            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(title))

            r = self.scraper.get(url).content

            result = client.parseDOM(r, 'article', attrs={'id': 'post.+?'})
            if len(result) == 0: raise Exception()

            result = [(client.parseDOM(i, 'div', attrs={'class': 'movie-details'})[0], client.parseDOM(i, 'a', ret='href')[0]) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].replace('\t', '').strip().encode('utf-8'))]
            if len(result) == 0: raise Exception()

            if len(result) > 1:
                for i in result:
                    try:
                        r1 = self.scraper.get(i).content
                        result1 = re.findall('Release.+?category/year/(\d{4})\">', r1)[0]
                        if not result1 == year: raise Exception()
                        url = i
                    except:
                        pass
            else:
                url = result[0]

            r = self.scraper.get(url).content

            items = client.parseDOM(r, 'div', attrs={'class': 'content-area'})[0]
            items = client.parseDOM(items, 'iframe', ret='src')

            for item in items:
                try:
                    if 'youtube' in item: raise Exception()
                    valid, hoster = source_utils.is_host_valid(item, hostDict)
                    urls, host, direct = source_utils.check_directstreams(item, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': '1080p', 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
