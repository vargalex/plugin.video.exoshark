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
        self.domains = ['onlinefilmek.co', 'hdfilmek.com']
        self.base_link = 'https://onlinefilmek.co'
        self.search_link = '/filter-search/%s'
        self.host_link = 'http://filmek-online.com'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote(localtitle))
            r = client.request(query)
            result = r.split('</a>')

            result = [i for i in result if self.base_link + '/film/' in i]
            result = [(client.parseDOM(i, 'div', attrs={'class': 'small-12 columns text-left'})[0], i) for i in result]
            result = [(client.replaceHTMLCodes(i[0].replace('\n', '')), i[1]) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            result = [(re.search('\s*:\s*(\d{4})', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]
            url = client.parseDOM(result, 'a', ret='href')[0]

            return (url, '')
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
            localtvshowtitle = data['localtvshowtitle'] if 'localtvshowtitle' in data else title

            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote(localtvshowtitle))
            r = client.request(query)
            result = r.split('</a>')

            result = [i for i in result if self.base_link + '/sorozat/' in i]
            result = [(client.parseDOM(i, 'div', attrs={'class': 'small-12 columns text-left'})[0], i) for i in result]
            result = [(client.replaceHTMLCodes(i[0].replace('\n', '')), i[1]) for i in result]
            result = [(i[0].rsplit(':', 1)[0], i[1]) for i in result if '/%s-evad' % season in i[1]]
            result = [i[1] for i in result if cleantitle.get(localtvshowtitle) == cleantitle.get(i[0].encode('utf-8'))]
            url = client.parseDOM(result, 'a', ret='href')[0]

            return (url, episode)
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return 

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = client.request(url[0])

            result = client.parseDOM(r, 'div', attrs={'class': 'row\s*text-center'})[0]
            urlt = client.parseDOM(result, 'a', ret='href')[-1]

            r2 = client.request(urlt)

            if url[1].isdigit():
                result = client.parseDOM(r2, 'div', attrs={'class': 'accordion-episodes'})
                result = [i for i in result if re.search('(?:d|den)\s*(\d+)\s*', client.parseDOM(i, 'a')[0]).group(1) == url[1]]
                if len(result) == 0: raise Exception()
                items = client.parseDOM(result, 'div', attrs={'class': 'panel\s*'})

            else: items = client.parseDOM(r2, 'div', attrs={'class': 'panel\s*'})

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for i in items:
                try:
                    itemreg = re.search('(?s)link_share\s*(?:link-fix2|)\'><a.+?>([^<>]+)<\/a>.+?<img.+?alt=\'([^\']+)\'.+?<a href=\'((?:watch[^\']+)|http[^\']+)', i)
                    if itemreg == None: itemreg = re.search('(?s)link_share\s*(?:link-fix2|)"><a.+?>([^<>]+)<\/a>.+?<img.+?alt="([^"]+)".+?<a href="((?:watch[^"]+)|http[^"]+)', i)
                    hostq = itemreg.group(1)
                    host, q = hostq.split('-')
                    host = host.rsplit('.', 1)[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    if 'CAM' in q: quality = 'CAM'
                    elif 'HD' in q: quality = 'HD'
                    else: quality = 'SD'
                    l = itemreg.group(2)
                    if 'szinkron' in l: info = 'szinkron'
                    else: info = ''
                    url = itemreg.group(3)
                    if url.startswith('watch'): url = self.host_link + '/' + url
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources

    def resolve(self, url):
        location = ''
        try:
            r = client.request(url, output='headers', redirect=False).headers
            try: location = [i.replace('Location:', '').strip() for i in r if 'Location:' in i][0]
            except: location = client.request(url)
            if self.host_link + '/watch-embed' in location:
                location = client.request(location)
                try: location = client.parseDOM(location, 'iframe', ret='src')[0]
                except: location = client.parseDOM(location, 'IFRAME', ret='SRC')[0]
            if not location.startswith('http'): raise Exception()
            url = client.replaceHTMLCodes(location)
            url = re.sub(r'^"|"$', '', url).strip()
            try: url = url.encode('utf-8')
            except: pass
            return url
        except: 
            return