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
        domains_ = ['c3JuZXQuZXU=']
        self.domains = [x.decode('base64') for x in domains_]
        self.base_link = 'aHR0cDovL3NybmV0LmV1'.decode('base64')


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            r = self.base_link + '/api/search.json'
            r_cache = cache.get(client.request, 120, r)
            result = json.loads(r_cache)
            result = [i for i in result if cleantitle.get(i['cat_eng'].encode('utf-8')) == cleantitle.get(title)]
            if not len(result) == 1: raise Exception()

            url1 = urlparse.urljoin(self.base_link, '/%s-online' % result[0]['url'].encode('utf-8'))

            r = client.request(url1, mobile=True)
            if not 'loop-content owl-carousel2 hide' in r: raise Exception()
            result = client.parseDOM(r, 'div', attrs={'class': 'loop-content owl-carousel2 hide'})
            result = client.parseDOM(result, 'div', attrs={'class': 'video'})
            result = [(re.search('(\d+)\.\s*\\xc9vad\s*\d+\.\s*Epiz\\xf3d[^"]+"\s*href="', i).group(1), i) for i in result]
            result = [i[1] for i in result if season == i[0]]
            if len(result) == 0: raise Exception()
            result = [(re.search('\d+\.\s*\\xc9vad\s*(\d+)\.\s*Epiz\\xf3d[^"]+"\s*href="', i).group(1), i) for i in result]
            result = [i[1] for i in result if episode == i[0]]
            if not len(result) == 1: raise Exception()

            urlr = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, urlr)
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            headers = {'Referer': url}

            r = client.request(url, mobile = True)
            urlr = client.parseDOM(r, 'textarea', attrs={'name': 'embed-this'})[0]
            urlr = client.parseDOM(urlr, 'iframe', ret='src')[0]
            if urlr.startswith('//'): urlr = 'http:' + urlr

            r1 = client.request(urlr, headers=headers, mobile=True)
            result = client.parseDOM(r1, 'div', attrs={'id': 'selector'})[0]
            items = re.findall('href="([^"]+)".+?center">([^<>]+)<', result)

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in items:
                try:
                    host = item[1].split('(', 1)[0]
                    host = host.strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = item[0]
                    url = client.replaceHTMLCodes(url)
                    if url.startswith('/embed'): url = self.base_link + url
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': 'SD', 'language': 'hu', 'info': 'szinkron', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            headers = re.sub('&play=\w+', '', url)
            r = client.request(url, headers=headers, mobile=True)
            try: url = client.parseDOM(r, 'iframe', ret='src')[0]
            except: url = client.parseDOM(r, 'IFRAME', ret='SRC')[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return
