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
from resources.lib.modules import directstream
from resources.lib.modules import source_utils
from resources.lib.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['pandamovie.pw']
        self.base_link = 'https://pandamovie.pw'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
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

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            year = data['year']
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            url = self.search_link % urllib.quote_plus(title)

            if 'tvshowtitle' in data:
                url = urlparse.urljoin(self.base_link, '/tv' + url)
            else:
                url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content

            result = client.parseDOM(r, 'div', attrs={'id': 'main'})[0]
            result = client.parseDOM(result, 'div', attrs={'class': 'item cf item-post'})
            result = [(client.parseDOM(i, 'a', ret='href')[-1], client.parseDOM(i, 'a', ret='title')[-1]) for i in result]
            result = [(i[0], re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d+|3D)(\.|\)|\]|\s|)(.+|)', '', i[1]), re.findall('\(\s*(\d{4})\s*\)', i[1])[0]) for i in result]

            try:
                if 'tvshowtitle' in data:
                    url = [i[0] for i in result if cleantitle.get(i[1]) == cleantitle.get(title) and hdlr.lower() in i[0] and (year == i[2])][0]
                else:
                    url = [i[0] for i in result if cleantitle.get(i[1]) == cleantitle.get(title) and (year == i[2])][0]
            except:
                url = None

            if url == None: return sources

            r = self.scraper.get(url).content

            items = client.parseDOM(r, 'div', attrs={'id': 'pettabs'})[0]
            items = client.parseDOM(items, 'a', ret='href')

            for item in items:
                try:
                    valid, host = source_utils.is_host_valid(item, hostDict)
                    if valid: 
                        sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': item, 'info': '', 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url
