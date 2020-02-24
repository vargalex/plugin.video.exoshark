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
        self.domains = ['filmezek.com']
        self.base_link = 'http://filmezek.com'
        self.search_link = '/search_cat.php?film=%s&type=1'
        self.host_link = 'https://filmzona.me'


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

            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(localtitle))
            r = client.request(query)

            result = client.parseDOM(r, 'div', attrs={'class': 'col-lg-2 col-sm-3 col-xs-6'})
            result = [i for i in result if self.base_link + '/online-filmek/' in i]
            result = [(client.parseDOM(i, 'h5')[0], client.parseDOM(i, 'a', ret='href')[0]) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            for i in result:
                try:
                    r = client.request(i)
                    imdbi_id = re.findall('imdb.com/title/(tt\d+)', r)
                    if imdbi_id == imdb: break
                except:
                    pass

            url = re.findall('<a.+?href="([^"]+)"><button type="button"', r)[0]

            items = client.request(url)
            items = client.parseDOM(items, 'table', attrs={'class': 'table table-striped'})[0]
            items = client.parseDOM(items, 'tr')

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in items[1:]:
                try:
                    host = client.parseDOM(item, 'td')[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    info = []
                    l = client.parseDOM(item, 'td')[1].strip().lower()
                    if 'magyar szinkronos' in l.lower(): info.append('szinkron')
                    q = client.parseDOM(item, 'td')[2]
                    if q.lower() == 'hd': quality = 'HD'
                    elif 'cam' in q.lower() or q.lower() == 'mozis': quality = 'CAM'
                    else: quality = 'SD'
                    datatype = client.parseDOM(item, 'i', ret='data-mediatype')[0]
                    videodataid = client.parseDOM(item, 'i', ret='data-video_id')[0]
                    url = {'datatype': datatype, 'videodataid': videodataid}
                    url = urllib.urlencode(url)
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': ' | '.join(info), 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            urlr = urlparse.urljoin(self.host_link, '/ajax/load.php')
            r = client.request(urlr, post=url)
            url = re.sub(r'\\|"', '', r)
            return url
        except:
            return
