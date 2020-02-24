# -*- coding: utf-8 -*-

"""
    Covenant Add-on

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

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['view4u.co']
        self.base_link = 'http://view4u.co'
        self.search_link = '/search/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases))

            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        #filecrypt.cc
        return ''

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return

            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)
            r = r.replace('\n', ' ')
            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'fullstory'})
            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'row'})

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'inner'})

            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [i.attrs['href'].strip() for i in r]

            for link in r:
                valid, host = source_utils.is_host_valid(link, hostDict)
                if not valid: continue
                sources.append({'source': host, 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles):
        try:
            query = self.search_link % urllib.quote_plus(cleantitle.query(titles[0]))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]

            r = client.request(query)

            body = dom_parser.parse_dom(r, 'div', attrs={'class': 'content_body'})[1].content
            r = dom_parser.parse_dom(body, 'a', req='href')
            r = [(i.attrs['href'], i.content.lower().replace('<b>','').replace('</b>','')) for i in r if i]
            r = [i for i in r if '<' not in i[1]]

            r = [i[0] for i in r if cleantitle.get(i[1]) in t]

            if len(r) > 0 :
                return source_utils.strip_domain(r[0])
            return ""
        except:
            return
