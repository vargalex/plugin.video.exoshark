# -*- coding: utf-8 -*-

'''
    ExoShark Add-on // This scraper made by Covenant developer

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


import re, urllib, urlparse, json, traceback

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['watchseriesfree.to', 'seriesfree.to']
        self.base_link = 'https://seriesfree.to'
        self.search_link = 'https://seriesfree.to/search/%s'


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            query = self.search_link % urllib.quote_plus(cleantitle.query(tvshowtitle))
            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs={'class': 'separate'})
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'h2', attrs={'class': 'serie-title'})[0]) for i in result]

            try:
                url = [i[0] for i in result if cleantitle.get(i[1].rsplit('(', 1)[0]) == cleantitle.get(tvshowtitle) and year in i[1]][0]
            except:
                url = None

            if url == None: raise Exception()

            url = url.encode('utf-8')
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.urljoin(self.base_link, url)
            r = client.request(url)

            result = client.parseDOM(r, 'div', attrs={'class': '.+?seasons-grid'})[0]
            seasons = client.parseDOM(result, 'div', attrs={'itemprop': 'containsSeason'})
            seasons = [i for i in seasons if client.parseDOM(i, 'span', attrs={'itemprop': 'seasonNumber'})[0] == season in i][0]
            episodes = client.parseDOM(seasons, 'li', attrs={'itemprop': 'episode'})

            try:
                url = [client.parseDOM(i, 'a', ret='href')[0] for i in episodes if client.parseDOM(i, 'span', attrs={'itemprop': 'episodeNumber'})[0] == episode in i][0]
            except:
                url = None

            if url == None: raise Exception()

            url = url.encode('utf-8')
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)
            r = client.request(url)
            
            result = client.parseDOM(r, 'div', attrs={'class': 'links', 'id': 'noSubs'})[0]
            
            # items = client.parseDOM(result, 'tr')
            # links = re.compile('<tr\s*>\s*<td><i\s+class="fa fa-youtube link-logo"></i>([^<]+).*?href="([^"]+)"\s+class="watch',re.DOTALL).findall(result)
            items = re.findall('(?s)<tr.+?<\/i>([^<]+)<.+?href="([^"]+)"\s*class="watch', result)
            
            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]
            
            for item in items:
                try:
                    host = item[0].rsplit('.', 1)[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = urlparse.urljoin(self.base_link, item[1])
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            r = client.request(url)
            url = re.findall('href="([^"]+)"\s*class="action-btn', r)[0]
            return url
        except:
            return
