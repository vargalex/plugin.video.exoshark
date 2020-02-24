# -*- coding: utf-8 -*-

"""
    Lastship Add-on (C) 2017
    Credits to Exodus and Covenant; our thanks go to their creators

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
"""

import re
import urllib
import urlparse

from resources.lib.modules import cache
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser
from resources.lib.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['movie4k.io', 'movie4k.tv', 'movie.to', 'movie4k.me', 'movie4k.org', 'movie4k.pe', 'movie2k.cm', 'movie2k.nu', 'movie4k.am']
        self._base_link = None
        self.search_link = '/movies.php?list=search&search=%s'
        self.scraper = cfscrape.create_scraper()

    @property
    def base_link(self):
        if not self._base_link:
            self._base_link = cache.get(self.__get_base_url, 120, 'http://%s' % self.domains[0])
        return self._base_link

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search(imdb, [localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search(imdb, [title] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search(imdb, [localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle:
                url = self.__search(imdb, [tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if url:
                return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None:
                return

            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content

            seasonMapping = dom_parser.parse_dom(r, 'select', attrs={'name': 'season'})
            seasonMapping = dom_parser.parse_dom(seasonMapping, 'option', req='value')
            seasonIndex = [i.attrs['value'] for i in seasonMapping if season in i.content]
            seasonIndex = int(seasonIndex[0]) - 1

            seasons = dom_parser.parse_dom(r, 'div', attrs={'id': re.compile('episodediv.+?')})
            seasons = seasons[seasonIndex]
            episodes = dom_parser.parse_dom(seasons, 'option', req='value')

            url = [i.attrs['value'] for i in episodes if episode in i.content]
            if len(url) > 0:
                return url[0]
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources

            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content
            r = r.replace('\\"', '"')

            links = dom_parser.parse_dom(r, 'tr', attrs={'id': 'tablemoviesindex2'})

            for i in links:
                try:
                    host = dom_parser.parse_dom(i, 'img', req='alt')[0].attrs['alt']
                    host = host.split()[0].rsplit('.', 1)[0].strip().lower()
                    host = host.encode('utf-8')

                    valid, host = source_utils.is_host_valid(host, hostDict)
                    if not valid: continue

                    url = dom_parser.parse_dom(i, 'a', req='href')[0].attrs['href']
                    url = client.replaceHTMLCodes(url)
                    url = urlparse.urljoin(self.base_link, url)
                    url = url.encode('utf-8')

                    sources.append({'source': host, 'quality': 'SD', 'language': 'de', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            h = urlparse.urlparse(url.strip().lower()).netloc

            r = self.scraper.get(url).content
            r = r.rsplit('"underplayer"')[0].rsplit("'underplayer'")[0]

            u = re.findall('\'(.+?)\'', r) + re.findall('\"(.+?)\"', r)
            u = [client.replaceHTMLCodes(i) for i in u]
            u = [i for i in u if i.startswith('http') and not h in i]

            url = u[-1].encode('utf-8')
            if 'bit.ly' in url:
                url = self.scraper.get(url).url
            elif 'nullrefer.com' in url:
                url = url.replace('nullrefer.com/?', '')

            return url
        except:
            return

    def __search(self, imdb, titles, year):
        try:
            q = self.search_link % titles[0]
            q = urlparse.urljoin(self.base_link, q)

            t = [cleantitle.get(i) for i in set(titles) if i]

            r = self.scraper.get(q).content

            links = dom_parser.parse_dom(r, 'tr', attrs={'id': re.compile('coverPreview.+?')})
            tds = [dom_parser.parse_dom(i, 'td') for i in links]
            tuples = [(dom_parser.parse_dom(i[0], 'a')[0], re.findall('>(\d{4})', i[1].content)) for i in tds if 'ger' in i[4].content]

            tuplesSortByYear = [(i[0].attrs['href'], i[0].content) for i in tuples if year in i[1]]

            if len(tuplesSortByYear) > 0:
                tuples = tuplesSortByYear
            else:
                tuples = [(i[0].attrs['href'], i[0].content) for i in tuples]

            urls = [i[0] for i in tuples if cleantitle.get(i[1]) in t]

            if len(urls) == 0:
                urls = [i[0] for i in tuples if 'untertitel' not in i[1]]

            if len(urls) > 0:
                return source_utils.strip_domain(urls[0])
        except:
            return

    def __get_base_url(self, fallback):
        try:
            for domain in self.domains:
                try:
                    url = 'http://%s' % domain
                    r = self.scraper.get(url).content
                    r = dom_parser.parse_dom(r, 'meta', attrs={'name': 'author'}, req='content')
                    if r and 'movie4k.io' in r[0].attrs.get('content').lower():
                        return url
                except:
                    pass
        except:
            pass

        return fallback
