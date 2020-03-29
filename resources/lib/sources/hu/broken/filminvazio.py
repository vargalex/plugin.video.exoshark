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
        self.base_link = 'https://ncore.live'
        self.search_link = '?s=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = "%s/%s" % (self.base_link, self.search_link) % urllib.quote_plus(localtitle)
            r = client.request(query)
            resultItems = client.parseDOM(r, "div", attrs={"class": "result-item"})
            for resultItem in resultItems:
                #titleDiv = client.parseDOM(resultItem, "div", attrs={'class': 'title'})[0]
                #href = client.parseDOM(titleDiv, 'a', ret="href")[0]
                #movieTitle = client.parseDOM(titleDiv, 'a')[0]
                #meta = client.parseDOM(resultItem, "div", attrs={'class': 'meta'})
                #movieYear = client.parseDOM(meta, 'span', attrs={'class': 'year'})[0]
                #file.write("movietitle: %s, movieyear: %s\n" % (movieTitle, movieYear))
                #if cleantitle.get(localtitle) == cleantitle.get(movieTitle.encode('utf-8')):
                #    if int(year)-1<=int(movieYear)<=int(year)+1:# in years:
                #        file.close()
                #        return url
            return
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            r = client.request(url)

            linkButtonBox = client.parseDOM(r, "div", attrs={'class':'linkButtonBox'})[0]
            href = client.parseDOM(linkButtonBox, "a", ret="href")[0]
            r = client.request(href)

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
