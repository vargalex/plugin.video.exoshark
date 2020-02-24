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
        self.domains = ['netmozi.com']
        self.base_link = 'https://netmozi.com'
        self.search_link = '/?search=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'localtitle': localtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
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

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            imdb = data['imdb']
            if 'tvshowtitle' in data:
                season, episode = data['season'], data['episode'] 
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = urlparse.urljoin(self.base_link, self.search_link % imdb)
            r = client.request(query, output='extended')
            headers = r[3]
            headers.update({'Cookie': r[2].get('Set-Cookie'), 'Referer': query})
            r = r[0]
            result = client.parseDOM(r, 'div', attrs={'class': 'col-sm-4 col_main'})[0]
            if len(result) == 0: raise Exception()

            url = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, url)
            if 'tvshowtitle' in data:
                url = url + '/s%s/e%s' % (season, episode)

            r = client.request(url, headers=headers)

            if 'tvshowtitle' in data:
                result = client.parseDOM(r, 'div', attrs={'class': 'tab-pane active'})
                result = [(re.search('<h4.+?>\s*(\w.+)\s*<\/h4>', i).group(1), i) for i in result]
                result = [i[1] for i in result if u'%s. \xe9vad %s. r\xe9sz' % (season, episode) in i]
                if len(result) == 0: raise Exception()
                result = client.parseDOM(result, 'table', attrs={'class': 'table table-responsive'})[0]
            else:
                result = client.parseDOM(r, 'table', attrs={'class': 'table table-responsive'})[0]

            items = result.split('</tr>')

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in items:
                try:
                    itemreg = re.search('(?s)(\/details\/openLink\/\d+).+?td>\s*<td>([^<>]+)<.+?<td>([^<>]+)', item)
                    lreg = re.search('(?s)pic\/(.+?<img src=".+?)\.', item).group(1)
                    host = itemreg.group(3)
                    host = host.rsplit('.', 1)[0].replace('www.', '').strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    q = itemreg.group(2)
                    if 'DVD' in q: quality = 'SD'
                    elif q =='HD': quality = 'HD'
                    elif 'CAM' in q or '(mozis)' in q or q == 'TS': quality = 'CAM'
                    else: quality = 'SD'
                    l = re.sub(r'(?s)(\..+?pic\/)', '', lreg).strip()
                    if l == 'hungarysubtitle' or 'usa' in l or 'uk-hu' in l: info = ''
                    else: info = 'szinkron'
                    url = itemreg.group(1)
                    url = client.replaceHTMLCodes(url)
                    url = self.base_link + url
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            r = client.request(url, output='geturl', redirect=True)
            r = r.rsplit('?l=', 1)[-1].strip()
            r = r.decode('base64')
            url = client.replaceHTMLCodes(r)
            url = url.encode('utf-8')
            return url
        except: 
            return
