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
from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['vmovee.xyz', 'vmovee.ws']
        self.base_link = 'https://vmovee.ws'
        self.search_link = '/search?x=0&y=0&q=%s'
        self.search_episode_link = '/vme-app/vme-includes/VME.php?season_id=%s'
        self.episode_link = '/vme-app/vme-includes/VME.php?episode_id=%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(title))

            r = self.scraper.get(query).content
            result = client.parseDOM(r, 'div', attrs={'id': 'feed'})[0]
            result = client.parseDOM(result, 'div', attrs={'class': 'movie-element.+?'})
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'div', attrs={'class': 'movie_box_title'})[0], re.findall('>\s*(\d{4})\s*<', i)[0]) for i in result]

            try:
                url = [i[0] for i in result if cleantitle.get(i[1]) == cleantitle.get(title) and (year == i[2])][0]
            except:
                url = None

            return url, 'movie'
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            tvshowtitle = data['tvshowtitle']
            year = data['year']

            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(tvshowtitle))

            r = self.scraper.get(query).content
            result = client.parseDOM(r, 'div', attrs={'id': 'feed'})[0]
            result = client.parseDOM(result, 'div', attrs={'class': 'movie-element.+?'})
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'div', attrs={'class': 'movie_box_title'})[0], re.findall('>\s*(\d{4})\s*<', i)[0]) for i in result]
            try:
                url = [i[0] for i in result if cleantitle.get(i[1]) == cleantitle.get(tvshowtitle) and (year == i[2])][0]
            except:
                url = None

            r = self.scraper.get(url).content
            result = client.parseDOM(r, 'div', attrs={'class': 'player'})[0]
            result = re.findall('<a id="epBtn"[^<>]+onclick="([^"]+)"', result)

            season_ids = [re.findall('(\d+)', i)[0] for i in result]
            season_len = [str(i+1) for i in range(len(season_ids))]
            seasonsDict = dict(zip(season_len, season_ids))
            season_id = seasonsDict[season]

            query = urlparse.urljoin(self.base_link, self.search_episode_link % season_id)

            r = self.scraper.get(query).content
            result = re.findall('(?s)>\s*(\d+)\s*<\/span.+?onclick="([^"]+)"', r)
            result = [(i[0], re.findall('(\d+)', i[1])[0]) for i in result]
            episodeDict = dict(result)
            episode_id = episodeDict[episode]

            url = urlparse.urljoin(self.base_link, self.episode_link % episode_id)

            return url, 'tvshow'
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url[0] == None: return

            content_type = url[1]

            r = self.scraper.get(url[0]).content

            if content_type == 'movie':
                items = re.findall('"src","([^"]+)"\),\$\("body"\)', r)
                if items == []: items = re.findall('"([^"]+litaurl.com[^"]+)"', r)
                items = ['http:' + i for i in items if not i.startswith('http')]
            else:
                items = re.findall('iframe src="([^"]+)"', r)

            for item in items:
                if content_type == 'movie': link = self.scraper.get(item).url
                else: link = item
                valid, host = source_utils.is_host_valid(link, hostDict)
                if valid: sources.append({'source': host, 'quality': '720p', 'language': 'en', 'url': link, 'info': '', 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources


    def resolve(self, url):
        return url
