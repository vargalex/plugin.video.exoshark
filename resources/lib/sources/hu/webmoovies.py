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
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['webmoovies.com']
        self.base_link = 'http://webmoovies.com'
        self.search_link = '/ajax/search.php'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = None

            post = urllib.urlencode({'q': title, 'limit': '5'})
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query, post = post)

            result = json.loads(r)
            result = [i for i in result if 'movie' in i['meta'].lower()]
            result = [(i['title'], i['permalink']) for i in result]

            for i in result:
                try:
                    t = re.findall('\(([^\)]+)', i[0])[0]
                    t = t.strip().encode('utf-8')
                    if t.isdigit():
                        if t == year and cleantitle.get(i[0].split('(')[0].strip().encode('utf-8')) == cleantitle.get(localtitle):
                            url = i[1]; break
                    else:
                        if cleantitle.get(t) == cleantitle.get(title):
                            url = i[1]; break
                except:
                    pass

            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


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

            post = urllib.urlencode({'q': title, 'limit': '5'})
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query, post = post)
            result = json.loads(r)

            result = [i for i in result if 'tv show' in i['meta'].lower()]
            result = [i for i in result if cleantitle.get(title) in cleantitle.get(i['title'].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            urlpri = result[0]['permalink'].encode('utf-8')
            urlsec = '/season/%s/episode/%s'

            url = urlpri + urlsec % (season, episode)
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf8')
            except: pass

            result = client.parseDOM(r, 'div', attrs={'id': 'link_list'})[0]
            result = result.split('<div class="span-16')

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    host = client.parseDOM(item, 'span')[0].strip().lower()
                    host = host.split('.', 1)[0]
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if (not host in hostDict or host == 'youtube.com'): raise Exception()
                    host = host.encode('utf-8')
                    url = client.parseDOM(item, 'a', ret='href')
                    url = [i for i in url if i.startswith('http')][0]
                    url = url.encode('utf-8')
                    l = re.search('images\/([a-zA-Z]+)', item).group(1).lower()
                    info = 'szinkron' if l == 'hun' else ''
                    
                    sources.append({'source': host, 'quality': 'SD', 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            url = re.search('//adf.ly/[0-9]+/(.*)', url).group(1)
            if not url.startswith('http'): url = 'http://' + url
            return url
        except: 
            return
