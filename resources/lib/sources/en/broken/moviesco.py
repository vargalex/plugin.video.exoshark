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
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['moviesco.cc']
        self.base_link = 'http://moviesco.cc'
        self.search_link = '/search?q=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = cleantitle.normalize(title)
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(t)))
            r = client.request(query)

            result = client.parseDOM(r, 'div', attrs={'class': 'showEntities.+?'})[0]
            result = client.parseDOM(r, 'div', attrs={'id': 'movie-\d+'})
            result = [i for i in result if not '<div class="movieTV">' in i]
            result = [(client.parseDOM(i, 'a', ret='href')[-1], client.parseDOM(i, 'a')[-1]) for i in result]

            urls = [urlparse.urljoin(self.base_link, i[0]) for i in result if cleantitle.get(i[1]) == cleantitle.get(title)]
            if len(urls) > 1:
                for u in urls:
                    r = client.request(u)
                    yr = re.findall('showValueRelease">\s*(\d{4})\s*<', r)[0]
                    if yr == year: url = r
            elif len(urls) == 1:
                url = urls[0]
            else:
                raise Exception()

            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return  


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            tvshowtitle = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            if 'year' in data: year = data['year']

            t = cleantitle.normalize(tvshowtitle)
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.getsearch(t)))
            r = client.request(query)

            result = client.parseDOM(r, 'div', attrs={'class': 'showEntities.+?'})[0]
            result = client.parseDOM(r, 'div', attrs={'id': 'movie-\d+'})
            result = [i for i in result if '<div class="movieTV">' in i]
            result = [(client.parseDOM(i, 'a', ret='href')[-1], client.parseDOM(i, 'a')[-1]) for i in result]

            show_url = [urlparse.urljoin(self.base_link, i[0]) for i in result if cleantitle.get(i[1]) == cleantitle.get(tvshowtitle)][0]
            r = client.request(show_url)

            result = client.parseDOM(r, 'div', attrs={'id': 'season%s' % season})[0]
            result = zip(client.parseDOM(result, 'h3'), client.parseDOM(result, 'div', attrs={'class': 'table table-striped tableLinks'}))

            url = [i[1] for i in result if 'season %s serie %s' % (season, episode) in i[0].lower()][0]

            return url
        except:
            return  


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            if url.startswith('http'):
                r = client.request(url)
                items = client.parseDOM(r, 'div', attrs={'class': 'linkTr'})
            else:
                items = client.parseDOM(url, 'div', attrs={'class': 'linkTr'})

            for item in items:
                try:
                    url = client.parseDOM(item, 'div', attrs={'class': 'linkHidden linkHiddenUrl'})[0]
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if valid:
                        url = client.replaceHTMLCodes(url)
                        url = url.encode('utf-8')
                        qual = client.parseDOM(item, 'div', attrs={'class': 'linkQualityText'})[0]
                        if any(x in qual.lower() for x in ['ts', 'cam']): quality = 'CAM'
                        elif any(x in qual.lower() for x in ['hd', '720p']): quality = '720p'
                        else: quality = 'SD'
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': '', 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url
