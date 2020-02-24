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


import re, urllib, urlparse, traceback
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['vioozgo.org']
        self.base_link = 'http://vioozgo.org'
        self.search_link = '/search?q=%s&s=t'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:    
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(title))
            r = client.request(query)

            result = client.parseDOM(r, 'div', attrs={'class': 'film boxed film_grid'})
            result = [(client.parseDOM(i, 'h3')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()
            
            result = [(re.search('Year\s*:\s*<.+?>\s*(\d{4})\s*<\/a>', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]
            if not len(result) == 1: raise Exception()

            url = client.parseDOM(result, 'a', ret='href')[0]
            url = url.encode('utf-8')
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = client.request(url)

            result = client.parseDOM(r, 'div', attrs={'class': 'contenu'})[-1]
            items = re.findall('(?s)a href="([^"]+)".+?<span class="display-name" style="[^"]+">(.+?)<\/span>', result)

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]         

            for item in items:
                try: 
                    host = item[1]
                    host = host.strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = item[0]
                    if url.startswith('/go/aHR0c'):
                        url = url.split('/')[-1]
                        url = url.decode('base64')
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'info': '', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
