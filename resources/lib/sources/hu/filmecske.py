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


import re, urllib, urlparse, json, traceback
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmecske.hu']
        self.base_link = 'https://filmecske.hu'
        self.search_link = '/film-kereso/itemlist/filterfork2?option=com_k2&view=itemlist&task=filterfork2&format=json&mid=800&Itemid=834&%s'


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

            years = cache.get(self.get_years, 720)
            year_id = [i[0] for i in years if year == i[1]][0]

            query = urllib.urlencode({'f[g][text]': localtitle, 'f[g][tags][]': year_id})
            query = urlparse.urljoin(self.base_link, self.search_link % query)
            r = client.request(query)
            result = json.loads(r)
            if result['total'] == 0: raise Exception()

            result = client.parseDOM(result['items'], 'div', attrs = {'class': 'moduleItemIntrotext'})
            result = [(client.parseDOM(i, 'img', ret='alt')[0].split('- online')[0].strip(), client.parseDOM(i, 'a', ret='href')[0]) for i in result]
            result = [(client.replaceHTMLCodes(i[0]), i[1]) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8')) or cleantitle.get(title) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            query = urlparse.urljoin(self.base_link, result[0])
            r = client.request(query)

            urlr = client.parseDOM(r, 'div', attrs = {'class': 'tovabb'})[0]
            urlr = client.parseDOM(urlr, 'a', ret='href')[0]

            r1 = client.request(urlr)

            result = client.parseDOM(r1, 'table', attrs = {'class': 'tablazat'})[0]
            result = client.parseDOM(result, 'tr')

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    host = client.parseDOM(item, 'td', attrs={'class': 'oszlop2'})[0]
                    host = client.parseDOM(host, 'img', ret='src')[0].rsplit('/')[-1].split('.')[0]
                    host = host.strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = 'http:' + client.parseDOM(item, 'a', ret='href')[0].split(':')[-1]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    q = client.parseDOM(item, 'td', attrs={'class': 'oszlop_minoseg'})[0]
                    q = client.parseDOM(q, 'a', ret='title')[0].lower()
                    if any(x in q for x in ['kamer', 'r5', 'cam']): quality = 'CAM'
                    elif any(x in q for x in ['dvdrip', 'bdrip']): quality = 'SD'
                    else: quality = 'SD'
                    l = client.parseDOM(item, 'td', attrs={'class': 'oszlop1'})[0]
                    l = client.parseDOM(l, 'img', ret='src')[0].rsplit('/')[-1].split('.')[0]
                    info = 'szinkron' if l == 'hu-hu' else ''
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            src = client.request(url)
            try: url = client.parseDOM(src, 'iframe', ret='src')[-1]
            except: url = client.parseDOM(src, 'IFRAME', ret='SRC')[-1]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_years(self):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link.split('/itemlist')[0])
            years = client.request(query)
            years = client.parseDOM(years, 'select', attrs = {'id': 'field_tags_800'})
            years = client.parseDOM(years, 'option', ret='value'),client.parseDOM(years, 'option')
            years = zip(years[0], years[1])
            return years
        except:
            return
