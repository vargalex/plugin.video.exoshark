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
from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filminvazio.net']
        self.base_link = 'https://filminvazio.net'
        self.search_link = '/search/%s/feed/rss2/'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'localtitle': localtitle, 'year': year}
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

            title = data['title']
            localtitle = data['localtitle']
            year = data['year']

            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(localtitle))
            r = client.request(query)

            result = client.parseDOM(r, 'item')
            if len(result) == 0: raise Exception()
            result = [(client.parseDOM(i, 'title')[0], client.parseDOM(i, 'link')[0]) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            for i in result:
                try:
                    r = client.request(i)
                    y = client.parseDOM(r, 'h1')[0]
                    y = re.findall('(\d{4})', y)[0]
                    if year == y: break
                except:
                    pass

            items = client.parseDOM(r, 'div', attrs={'class': 'fix-table'})[0]
            items = client.parseDOM(items, 'tr')
            if len(items) == 0: raise Exception()

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in items[1:]:
                try:
                    host = client.parseDOM(item, 'a')[0]
                    host = re.sub('(<[^<>]+>)', '', host)
                    host = host.split('.')[0].lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = client.parseDOM(item, 'a', ret = 'href')[0]
                    url = url.encode('utf-8')
                    q = client.parseDOM(item, 'td')[1].strip().lower()
                    if q == 'hd': quality = 'HD'
                    elif 'ts' in q or 'cam' in q: quality = 'CAM'
                    else: quality = 'SD'
                    l = client.parseDOM(item, 'td')[2].strip().lower()
                    info = []
                    if l == 'magyar' or 'szinkron' in l: info.append('szinkron')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': ' | '.join(info), 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            r = client.request(url)
            url = client.parseDOM(r, 'a', ret='href')[-1]
            return url
        except:
            return
