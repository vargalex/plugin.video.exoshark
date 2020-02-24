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
import base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['movie4k.lt']
        self.base_link = 'http://www.movie4k.lt'
        self.search_link = '/search/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources
            r = client.request(url)

            links = dom_parser.parse_dom(r, 'div', attrs={'id': 'tab-plot_german'})
            links = dom_parser.parse_dom(links, 'tbody')
            links = dom_parser.parse_dom(links, 'tr')
            links = [(dom_parser.parse_dom(i,'a')[0],
                      dom_parser.parse_dom(i,'td', attrs={'class': 'votesCell'})[0])
                     for i in links if "gif" in i.content]

            links = [(i[0][1], i[0].attrs['href'], source_utils.get_release_quality(i[1].content)) for i in links]

            for hoster, link, quality in links:
                valid, hoster = source_utils.is_host_valid(hoster, hostDict)

                if not valid:
                    continue
                if '?' in link:
                    link = urlparse.urljoin(self.base_link, url, link)
                sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': link, 'direct': False, 'debridonly': False, 'checkquality': True})

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            if self.base_link in url:
                r = client.request(url)
                s = re.findall("dingdong\('(.*?)'", r)[0]
                s = base64.b64decode(s)
                s = re.findall("src=\"(.*?)\"", s)[0]
                url = s.strip('/')
            else:
                return url

        except:
            return url

    def __search(self, titles, year):
        try:
            query = self.search_link % (urllib.quote_plus(urllib.quote_plus(cleantitle.query(titles[0]))))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]

            r = client.request(query)

            links = dom_parser.parse_dom(r, 'a', attrs={'class': 'coverImage'})
            links = [(i.attrs['href'], re.findall('(.*?)\(', i.attrs['title'])[0]) for i in links if year in i.content]
            for i in links:
                title = i[1]
                title = cleantitle.get(title)
                if title in t:
                    return i[0]
                else:
                    continue
            return ""
        except:
            return
