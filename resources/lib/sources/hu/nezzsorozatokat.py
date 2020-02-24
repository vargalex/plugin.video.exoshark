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
from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['nezzsorozatokat.info']
        self.base_link = 'http://nezzsorozatokat.info'
        self.search_link = '/js/autocomplete_ajax.php?term=%s'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            episode = episode.zfill(2)
            season = season.zfill(2)

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(title))
            r = client.request(query)
            result = json.loads(r)

            result = [i for i in result if cleantitle.get(title) in cleantitle.get(i['label'].encode('utf-8'))]
            result = [i for i in result if 'S%sE%s' % (season, episode) in i['label']]
            if len(result) == 0: raise Exception()

            url = urlparse.urljoin(self.base_link, '/?' + result[0]['id'])
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

            result = client.parseDOM(r, 'div', attrs={'id': 'main'})
            result = result[0].split('<p class')
            if len(result) == 0: raise Exception() 

            for item in result:
                try:
                    try: id = client.parseDOM(item, 'div', ret='load-id')[0]
                    except: id = client.parseDOM(item, 'div', ret='sorsz')[0]
                    query = urlparse.urljoin(self.base_link, '/videobetolt.php?id=' + id)
                    r = client.request(query, timeout='10')
                    try: url = client.parseDOM(r, 'iframe', ret='src')[0]
                    except: url = client.parseDOM(r, 'IFRAME', ret='SRC')[0]
                    url = url.encode('utf-8')
                    host = urlparse.urlparse(url.strip().lower()).netloc
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    l = client.parseDOM(item, 'span', attrs={'class': 'doboz'})[0]
                    info = 'szinkron' if 'magyar szinkron' in l.lower() else ''
                    sources.append({'source': host, 'quality': 'SD', 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
