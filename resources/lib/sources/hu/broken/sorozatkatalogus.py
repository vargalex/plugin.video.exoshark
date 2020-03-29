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
        self.domains = ['sorozatkatalogus.cc']
        self.base_link = 'https://sorozatkatalogus.cc'
        self.search_link = '/wp-admin/admin-ajax.php'


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

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
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

            tvshowtitle = data['tvshowtitle']
            season, episode = data['season'], data['episode']
            imdb = data['imdb']

            query = urlparse.urljoin(self.base_link, self.search_link)
            post = urllib.urlencode({'action': 'ajaxsearchlite_search', 'aslp': imdb, 'asid': '1', 'options': 'qtranslate_lang=0&set_intitle=None&set_incontent=None&set_inposts=None&categoryset%5B%5D=2&categoryset%5B%5D=43&categoryset%5B%5D=160&categoryset%5B%5D=3&categoryset%5B%5D=157&categoryset%5B%5D=4&categoryset%5B%5D=44&categoryset%5B%5D=5&categoryset%5B%5D=6&categoryset%5B%5D=7&categoryset%5B%5D=8&categoryset%5B%5D=9&categoryset%5B%5D=10&categoryset%5B%5D=11&categoryset%5B%5D=12&categoryset%5B%5D=13&categoryset%5B%5D=81&categoryset%5B%5D=15&categoryset%5B%5D=14&categoryset%5B%5D=16'})
            r = client.request(query, post=post, XHR=True)

            result = client.parseDOM(r, 'div', attrs={'class': 'asl_content'})
            if len(result) == 0: raise Exception()

            url = client.parseDOM(result, 'a', ret='href')[0]

            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf8')
            except: pass
            result = client.parseDOM(r, 'div', attrs={'class': 'su-box su-box-style-default'})
            result = [(client.parseDOM(i, 'div', attrs={'class': 'su-box-title'})[0].strip(), i) for i in result]
            result = [i for i in result if 'vad' in i[0]]
            result = [i[1] for i in result if re.findall('(?:0|)(\d+)', i[0])[0] == season]
            if not len(result) == 1: raise Exception()

            episodes = client.parseDOM(result[0], 'tr')
            episodes = [(client.parseDOM(i, 'span')[0], i) for i in episodes]
            episodes = [i[1] for i in episodes if re.findall('(?:0|)(\d+)', i[0])[0] == episode]
            if not len(episodes) == 1: raise Exception()

            url = client.parseDOM(episodes[0], 'a', ret='href')[0]

            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf8')
            except: pass

            result = client.parseDOM(r, 'div', attrs={'class': 'entry-content'})[0]
            result = client.parseDOM(result, 'td')

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]
            host_corr = ['flashx', 'vidto']

            for item in result:
                try:
                    l = client.parseDOM(item, 'img', ret='src')[0]
                    l = l.rsplit('/', 1)[1].split('.')[0].strip()
                    host = ''.join(c for c in l if c.islower())
                    try: host = [i for i in host_corr if i in host][0]
                    except: pass
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    url = client.parseDOM(item, 'a', ret='href')[0]
                    url = url.encode('utf-8')
                    info = 'szinkron' if 'H' in l[0] else ''
                    sources.append({'source': host, 'quality': 'SD', 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            url = client.parseDOM(r, 'div', attrs={'class': 'tovabb'})[0]
            if not url: raise Exception()
            r = client.request(client.parseDOM(url, 'a', ret='href')[0])   
            result2 = client.parseDOM(r, 'tr', attrs={'class': 'sor3'})

            for item in result2:
                try:
                    host = client.parseDOM(item, 'img', ret='src')[1]
                    host = host.rsplit('/', 1)[1].split('.')[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    l = client.parseDOM(item, 'img', ret='src')[0]
                    l = l.rsplit('/', 1)[1].split('.')[0].strip().lower()
                    info = 'szinkron' if l == 'hu-hu' else ''
                    url = client.parseDOM(item, 'a', ret='href')[0]
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': 'SD', 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass   

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            url = url.split('http')[-1]
            r = client.request('http' + url)
            result = client.parseDOM(r, 'div', attrs={'class': 'entry-content'})[0]
            url = client.parseDOM(result, 'iframe', ret='src')[0]
            if url.startswith('//'): url = 'http:' + url
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return
