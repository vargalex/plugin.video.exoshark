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

import base64
import json
import re
import urllib
import urlparse

from resources.lib.modules import anilist
from resources.lib.modules import cfscrape
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils
from resources.lib.modules import tvmaze


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['foxx.to']
        self.base_link = 'http://foxx.to'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            if not url and source_utils.is_anime('movie', 'imdb', imdb): url = self.__search([anilist.getAlternativTitle(title)] + source_utils.aliases_to_array(aliases), year)
            
            return url
        except:
            return ""

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:

            linkAndTitle = self.__search([tvshowtitle, localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            aliases = source_utils.aliases_to_array(aliases)

            if not tvshowtitle and source_utils.is_anime('show', 'tvdb', tvdb): linkAndTitle = self.__search([tvmaze.tvMaze().showLookup('thetvdb', tvdb).get('name')] + source_utils.aliases_to_array(aliases), year)

            return linkAndTitle
        except:
            return ""

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            r = self.scraper.get(url).content

            if season == 1 and episode == 1:
                season = episode = ''

            r = dom_parser.parse_dom(r, 'ul', attrs={'class': 'episodios'})
            r = dom_parser.parse_dom(r, 'a', attrs={'href': re.compile('[^\'"]*%s' % ('-%sx%s' % (season, episode)))})[0].attrs['href']
            return source_utils.strip_domain(r)
        except:
            return ""

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources
            url = urlparse.urljoin(self.base_link, url)
            temp = self.scraper.get(url)
            link = re.findall('iframe\ssrc="(.*?view\.php.*?)"', temp.content)[0]
            if link.startswith('//'):
                link = "https:" + link

            r = self.scraper.get(link, headers={'referer': url}).content
            phrase = re.findall('jbdaskgs = \'(.*)?\'', r)[0]
            links = json.loads(base64.b64decode(phrase))

            [sources.append({'source': 'CDN', 'quality': i['label'] if i['label'] in ['720p', '1080p'] else 'SD', 'language': 'de', 'url': i['file'], 'direct': True,
                         'debridonly': False}) for i in links]
            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles, year):
        try:
            query = self.search_link % (urllib.quote_plus(titles[0]))
            query = urlparse.urljoin(self.base_link, query)

            r = self.scraper.get(query).content
            dom_parsed = dom_parser.parse_dom(r, 'div', attrs={'class': 'details'})
            links = [(dom_parser.parse_dom(i, 'a')[0], dom_parser.parse_dom(i, 'span', attrs={'class' : 'year'})[0].content) for i in dom_parsed]

            r = sorted(links, key=lambda i: int(i[1]), reverse=True)  # with year > no year
            r = [x[0].attrs['href'] for x in r if int(x[1]) == int(year)]

            if len(r) > 0:
                return source_utils.strip_domain(r[0])
        except:
            return
