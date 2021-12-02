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
from resources.lib.modules import cfscrape
from resources.lib.modules import es_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmgo.cc']
        self.base_link = 'https://filmgo.cc'
        self.search_link = '/typeahead/%s'
        self.host_link = 'http://linkadatbazis.xyz'
        self.scraper = cfscrape.create_scraper()


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
            imdb = data['imdb']

            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote(localtitle))
            r = self.scraper.get(query).content
            if not r: raise Exception()

            result = json.loads(r)
            result = [i for i in result if i['type'] == 'movie']
            result = [i for i in result if cleantitle.get(i['title'].encode('utf-8')) == cleantitle.get(localtitle)]
            if len(result) == 0: raise Exception()

            cont = None

            for i in result:
                try:
                    cont = self.scraper.get(i['link']).content
                    imdb_id = re.findall('"imdb_id"\s*:\s*"([^"]+)"', cont)
                    if imdb_id == imdb: break
                except:
                    pass

            if cont == None: raise Exception()

            url1 = re.findall('a href="([^"]+)"[^<>]+>\s*<div class="link-box"', cont)[0]
            urlr = self.scraper.get(url1).url
            urlr = 'http' + urlr.split('http')[-1]
            r1 = self.scraper.get(urlr).content
            if 'var ysmm' in r1:
                ysmm = re.findall('var ysmm = \'(.*?)\';', r1)[0]
                urlr = es_utils.adfly_crack(ysmm)
                r1 = self.scraper.get(urlr).content

            items = client.parseDOM(r1, 'div', attrs={'class': 'szever'})[0]
            items = client.parseDOM(items, 'div', attrs={'class': 'tr'})

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in items:
                try:
                    item = item.replace('\n', '').replace('\t', '').replace('\r', '').replace("'", '"')
                    host = client.parseDOM(item, 'div', attrs={'class': 'tarhely'})[0]
                    host = host.lower().split('.', 1)[0].strip()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    l = client.parseDOM(item, 'img', ret='src')[0]
                    l = l.rsplit('/', 1)[-1].split('.', 1)[0].strip()
                    info = 'szinkron' if l == 'hu-hu' or l == 'lt' else ''
                    q = client.parseDOM(item, 'div', attrs={'class': 'minoseg'})[0]
                    q = q.lower()
                    if q == 'hd': quality = 'HD'
                    elif 'cam' in q or 'ts' in q or q == 'mozis': quality = 'CAM'
                    else: quality = 'SD'
                    url = client.parseDOM(item, 'a', ret='href')[0]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'url': url, 'info': info, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            if not url.startswith('http:'):
                url = urlparse.urljoin(self.host_link, url)
            r = self.scraper.get(url).content
            url = client.parseDOM(r, 'a', ret='href')[-1]
            url = 'http' + url.split('/http')[-1]
            return url
        except:
            return
