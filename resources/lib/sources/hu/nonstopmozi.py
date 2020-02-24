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
        self.language = ['hu']
        self.domains = ['nonstopmozi.hu']
        self.base_link = 'https://nonstopmozi.hu'
        self.search_link = '/online-filmek/kereses/%s'


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

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            localtitle = data['localtvshowtitle'] if 'localtvshowtitle' in data else data['localtitle']
            year = data['year']

            query = urlparse.urljoin(self.base_link, self.search_link % cleantitle.geturl(title))
            post = urllib.urlencode({'keres': title, 'submit': 'Keresés'})
            r = client.request(query, post=post)
            result = client.parseDOM(r, 'div', attrs={'class': 'col-md-2 w3l-movie-gride-agile'})

            result = [i for i in result if self.base_link + '/online-filmek/' in i]
            result = [(client.parseDOM(i, 'a', ret='title')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            result = [(re.search('>\((\d{4})\)<', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]
            url = client.parseDOM(result, 'a', ret='href')[0]

            r = client.request(url)

            result = client.parseDOM(r, 'table')[0]
            result = client.parseDOM(result, 'tr')

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result[1:]:
                try: 
                    itemreg = re.search('(?s)images\/lang\/([^\/\.]+)\..+?td align.+?>\s*(.+?)\s*<.+?images\/forras\/([^\/\.]+)\..+?href=\'([^\']+)', item)
                    host = itemreg.group(3)
                    host = host.strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    q = itemreg.group(2)
                    if 'mozis' in q.lower(): quality = 'CAM'
                    elif 'dvd' in q.lower(): quality = 'SD'  
                    elif 'hd' in q.lower(): quality = 'HD'
                    else: quality = 'SD'
                    l = itemreg.group(1)
                    l = l.strip().lower()
                    info = 'szinkron' if l == 'magyar' else ''
                    url = itemreg.group(4)
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            r = client.request(url)
            url = client.parseDOM(r, 'iframe', ret='src')[0]
            return url
        except:
            return
