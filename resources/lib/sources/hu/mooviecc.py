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
from resources.lib.modules import es_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['moovie.cc']
        self.base_link = 'https://moovie.cc'
        self.search_link = '/core/ajax/movies.php'
        self.host_link = 'http://www.filmbazis.org'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = cleantitle.getsearch(localtitle)
            t = urllib.quote_plus(t)
            query = urlparse.urljoin(self.base_link, self.search_link)
            s_query = 'type=search&query=keywords:%s|page:1' % localtitle
            headers = {'Origin': self.base_link, 'X-Requested-With': 'XMLHttpRequest',
                       'Referer': '%s/kereses/%s' % (self.base_link, t), 'Content-Type': 'application/x-www-form-urlencoded'}
            r = client.request(query, headers=headers, post=s_query)

            result = client.parseDOM(r, 'div', attrs={'id': 'movie_.+?'})
            result = [client.parseDOM(i, 'h2')[0] for i in result]
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0], re.findall('\((\d{4})\)', i)[0]) for i in result]
            try:
                url = [i[0] for i in result if cleantitle.get(i[1].encode('utf-8')) == cleantitle.get(localtitle) and (year == i[2])][0]
            except:
                url = None

            if url == None: raise Exception()

            query = urlparse.urljoin(self.base_link, url)
            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs={'class': 'streamBtn'})[0]
            query = client.parseDOM(result, 'a', ret='href')[0]
            query = 'http' + query.rsplit('http', 1)[-1]

            url = client.request(query, output='headers', redirect=False).dict['location']
            if not url.startswith('http'): url = self.host_link + url
            r = client.request(url)
            host_domain = urlparse.urlsplit(query).netloc
            result = client.parseDOM(r, 'tr', attrs={'class': 'jsPlay'})
            return result, host_domain
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
            if 'year' in data: year = data['year']

            t = cleantitle.getsearch(localtvshowtitle)
            t = urllib.quote_plus(t)
            query = urlparse.urljoin(self.base_link, self.search_link)
            s_query = 'type=search&query=keywords:%s|page:1' % localtvshowtitle
            headers = {'Origin': self.base_link, 'X-Requested-With': 'XMLHttpRequest',
                       'Referer': '%s/kereses/%s' % (self.base_link, t), 'Content-Type': 'application/x-www-form-urlencoded'}
            r = client.request(query, headers=headers, post=s_query)

            result = client.parseDOM(r, 'div', attrs={'id': 'movie_.+?'})
            result = [client.parseDOM(i, 'h2')[0] for i in result]
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0], re.findall('\((\d{4})\)', i)[0]) for i in result]
            try:
                url = [i[0] for i in result if cleantitle.get(i[1].encode('utf-8')) == cleantitle.get(localtvshowtitle) and (year == i[2])][0]
            except:
                url = None

            if url == None: raise Exception()

            query = urlparse.urljoin(self.base_link, url)

            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs={'class': 'streamBtn'})[0]
            query = client.parseDOM(result, 'a', ret='href')[0]
            query = 'http' + query.rsplit('http', 1)[-1]

            url = client.request(query, output='headers', redirect=False).dict['location']
            if not url.startswith('http'): url = self.host_link + '%s/%s-evad' % (url, season)
            r = client.request(url)
            host_domain = urlparse.urlsplit(query).netloc
            result = client.parseDOM(r, 'div', attrs={'class': 'seasonList'})
            result = client.parseDOM(result, 'div', attrs={'class': 'item'})
            result = [i for i in result if client.parseDOM(i, 'input', ret='id')[0] == episode]
            result = client.parseDOM(result, 'tr', attrs={'class': 'jsPlay'})
            if len(result) == 0:raise Exception()
            return result, host_domain
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            result = url[0]
            host_domain = url[1]
            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    host = client.parseDOM(item, 'td')[2].split('.')[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    q = client.parseDOM(item, 'span')[0].lower()
                    if ('mozis' in q or 'ts' in q or 'cam' in q): quality = 'CAM'
                    else: quality = 'SD'
                    l = client.parseDOM(item, 'img', ret='src')[0]
                    l = l.split('/')[-1].rsplit('.', 1)[0].strip().lower()
                    if (l == 'hu' or l == 'hu-hu'): info = 'szinkron'
                    else: info = ''
                    url = client.parseDOM(item, 'a', ret='href')[0]
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False, 'sourcecap': True})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        if '/http' in url:
            url = url.rsplit('/http', 1)[1]
            url = 'http' + url
        mvcc_cookie = client.request(url, output='cookie')
        try:
            r = client.request(url, cookie=mvcc_cookie)
            if 'captcha' in r:
                captcha_img = self.host_link + '/captchaimg.php'
                solution = es_utils.captcha_resolve(captcha_img, mvcc_cookie)
                postdata = urllib.urlencode({'captcha': solution, 'submit': 'Ok'})
                r = client.request(url, redirect=True, cookie=mvcc_cookie, post=postdata)
            result = client.parseDOM(r, 'div', attrs={'class':'embedHolder'})[0]
            try: url = client.parseDOM(result, 'iframe', ret='src')[0]
            except: url = client.parseDOM(result, 'a', ret='href')[-1]
            url = url.encode('utf-8')
            return url
        except:
            return
