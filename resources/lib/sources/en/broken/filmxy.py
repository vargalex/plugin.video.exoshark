# -*- coding: UTF-8 -*-

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

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['filmxy.ws', 'filmxy.me']
        self.base_link = 'https://www.filmxy.ws'
        self.search_link = '/?s=%s'


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

            if url == None: return

            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)
            title = data['title']
            year = data['year']

            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(title))

            r = client.request(query)

            result = client.parseDOM(r, 'div', attrs={'class': 'recent-posts'})[0]
            result = client.parseDOM(result, 'div', attrs={'class': 'single-post'})

            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'h2')[0]) for i in result]
            result = [(i[0], re.sub('(\s*\.|\s*\(|\s*\[|\s)(\d{4}|3D)(\.|\)|\]|\s|)(.+|)', '', i[1]), re.findall('\(\s*(\d{4})\s*\)', i[1])[0]) for i in result]
            try:
                url = [i[0] for i in result if cleantitle.get(i[1]) == cleantitle.get(title) and (year == i[2])][0]
            except:
                url = None

            if url == None: return sources

            r = client.request(url)

            try:
                wsrv = client.parseDOM(r, 'div', attrs={'class': 'watch-servers'})[0]
                wsrv = client.replaceHTMLCodes(wsrv)
                wsrv_items = client.parseDOM(wsrv.lower(), 'iframe', ret='src')
                for item in wsrv_items:
                    try:
                        valid, host = source_utils.is_host_valid(item, hostDict)
                        if valid: sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': item, 'info': '', 'direct': False, 'debridonly': False})
                    except:
                        pass
            except:
                pass

            url = re.findall('id="main-down"\s*href="([^"]+)"', r)[0]
            r = client.request(url)

            items = client.parseDOM(r, 'div', attrs={'class': 'link-panel row'})

            for item in items:
                try:
                    qual = client.parseDOM(item, 'h3', attrs={'class': 'panel-title'})[0]
                    if qual == '720p Links': quality = '720p'
                    elif qual == '1080p Links': quality = '1080p'
                    else: quality = 'SD'

                    links = client.parseDOM(item, 'a', ret='href')

                    for link in links:
                        try:
                            valid, host = source_utils.is_host_valid(link, hostDict)
                            if valid: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': '', 'direct': False, 'debridonly': False})
                        except:
                            pass
                except:
                    pass
            return sources   
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
