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


import re, urllib, urlparse, traceback, unicodedata
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
        self.sources_link = 'https://filminvazio.net/?p=%s'
        self.online_link = 'https://filminvazio.net/wp-admin/admin-ajax.php'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = "%s/%s\n" % (self.base_link, self.search_link) % urllib.quote_plus(localtitle)
            r = client.request(query).decode('iso-8859-1').encode('utf-8')
            resultItems = client.parseDOM(r, "div", attrs={"class": "result-item"})
            for resultItem in resultItems:
                titleDiv = client.parseDOM(resultItem, "div", attrs={'class': 'title'})[0]
                href = client.parseDOM(titleDiv, 'a', ret="href")[0]
                movieTitle = client.parseDOM(titleDiv, 'a')[0]
                meta = client.parseDOM(resultItem, "div", attrs={'class': 'meta'})
                movieYear = client.parseDOM(meta, 'span', attrs={'class': 'year'})[0]
                if cleantitle.get(localtitle.decode('iso-8859-1')) == cleantitle.get(movieTitle):
                    if int(year)-1<=int(movieYear)<=int(year)+1:# in years:
                        return href
            return
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            r = client.request(url)

            movieID = client.parseDOM(r, "div", attrs={'class':'linkButtonBox'}, ret="id")[0]
            r = client.request(self.sources_link % movieID)

            ul = client.parseDOM(r, "ul", attrs={'id': 'playeroptionsul'})[0].replace('\n', '').replace('</li>', '</li>\n')
            items =  re.findall(r'(?:.*)<li(?:.*)data-type=\'(.*)\'(?:.*)data-post=\'(.*)\'(?:.*)data-nume=\'([0-9]*)\'(?:.*)class=\'server\'>(.*)</span(?:.*)class=\'flag\'(.*)</span(?:.*)</li>(?:.*)', ul)
            for item in items:
                url_content = client.request(self.online_link, post="action=doo_player_ajax&post=%s&nume=%s&type=%s" % (item[1], item[2], item[0]))
                url = client.parseDOM(url_content, 'iframe', ret='src')[0]
                host = item[3]
                host = re.sub('(<[^<>]+>)', '', host)
                host = host.split('.')[0].lower()
                host = [x[1] for x in locDict if host == x[0]][0]
                if host in hostDict: 
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    info = ""
                    if "flags/hu" in item[4]:
                        info = "szinkron"
                    sources.append({'source': host, 'quality': 'SD', 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})

            fixTable = client.parseDOM(r, 'div', attrs={'class': 'fix-table'})[0]
            table = client.parseDOM(fixTable, 'table')[0]
            tbody = client.parseDOM(table, 'tbody')[0]
            items = client.parseDOM(tbody, 'tr')
            if len(items) == 0: raise Exception()

            for item in items:
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
                    r2 = client.request(url)
                    url = client.parseDOM(r2, 'a', ret='href')[-1]
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
            return url
        except:
            return
