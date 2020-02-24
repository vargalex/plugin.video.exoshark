# -*- coding: utf-8 -*-

"""
    Lastship Add-on (C) 2018
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

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['hdkino.to']
        self.base_link = 'https://hdkino.to'
        self.search_link = '/search/%s'
        self.stream_link = '/embed.php?video_id=%s&provider=%s'

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

            query = urlparse.urljoin(self.base_link, url)

            r = client.request(query)

            links = re.findall('data-video-id="(.*?)"\sdata-provider="(.*?)"', r)

            for id, hoster in links:
                valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                if not valid: continue

                sources.append({'source': hoster, 'quality': '720p', 'language': 'de', 'url': (id, hoster), 'direct': False, 'debridonly': False, 'checkquality': True})

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            link = self.stream_link % (url[0], url[1])
            link = urlparse.urljoin(self.base_link, link)
            content = client.request(link)
            return dom_parser.parse_dom(content, 'iframe')[0].attrs['src']

        except:
            return

    def __search(self, titles, year):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]

            for title in titles:
                query = self.search_link
                try:
                    title.encode('UTF-8')
                    query %= urllib.quote_plus(title)
                except:
                    query %= title.decode('UTF-8').encode('Windows-1252')

                query = urlparse.urljoin(self.base_link, query)

                r = client.request(query)

                links = dom_parser.parse_dom(r, 'div', attrs={'class': 'search_frame'})
                links = [dom_parser.parse_dom(i, 'a') for i in links]
                links = [(i[1], i[2]) for i in links]
                links = [(i[0].attrs['href'], re.findall('>(.*?)<', i[0].content)[0], i[1].content) for i in links]
                links = sorted(links, key=lambda i: int(i[2]), reverse=True)  # with year > no year
                links = [i[0] for i in links if cleantitle.get(i[1]) in t and year == i[2]]

                if len(links) > 0:
                    return source_utils.strip_domain(links[0])

            return
        except:
            return
