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
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmbaratok.org']
        self.base_link = 'http://filmbaratok.org'
        self.search_link = '/search/?%s'
        self.user = control.setting('filmbaratok.user')
        self.password = control.setting('filmbaratok.pass')


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

            if (self.user == '' or self.password == ''): raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['title']
            localtitle = data['localtitle']
            year = data['year']

            query = urllib.urlencode({'search_query': localtitle, 'tax_release-year[]': year})
            query = urlparse.urljoin(self.base_link, self.search_link % query)

            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs = {'class': 'resultado'})
            if len(result) == 0: raise Exception()
            result = [(client.parseDOM(i, 'a')[1], client.parseDOM(i, 'a', ret='href')[0]) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8')) or cleantitle.get(title) == cleantitle.get(i[0].encode('utf-8'))]
            if not len(result) == 1: raise Exception()

            url = result[0].encode('utf-8')

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            cookie = self.get_cookie()
            headers = {'Referer': url, 'Cookie': cookie}

            query = urlparse.urljoin(self.base_link, '/ajax/?q=url-list')
            
            r = client.request(query, headers=headers)
            try: r = r.decode('unicode-escape')
            except: pass
            result = r.split('<li>')

            for i in result:
                try:
                    host = client.parseDOM(i, 'span', attrs = {'class': 'op'})[0].split('<')[0].rsplit('.', 1)[0].lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    item = re.compile('click&0=([0-9]+).+?Nyelv.+?span>\s?(.+?)<.+?title.+?span>\s?(.+?)<').findall(i)[0]
                    if 'DVD' in item[2]: quality = 'SD'
                    elif 'Mozis' in item[2]: quality = 'CAM'
                    else: quality = 'SD'
                    if 'szinkron' in item[1]: info = 'szinkron'
                    else: info = ''
                    query = urlparse.urljoin(self.base_link, '/online-video/?id=%s' % (item[0]))
                    url = client.replaceHTMLCodes(query)
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
            cookie = self.get_cookie()
            headers = {'Referer': url, 'Cookie': cookie}
            src = client.request(url, headers=headers).lower()
            url = client.parseDOM(src, 'iframe', ret='src')[-1]
            return url
        except:
            return


    def get_cookie(self):
        try:
            login = urlparse.urljoin(self.base_link, '/login/')
            post = urllib.urlencode({'log': self.user, 'pwd': self.password, 'submit': 'Belépés', 'redirect_to': 'http://filmbaratok.org'})
            cookie = client.request(login, post=post, output='cookie', close=False)
            if not 'logged_in' in cookie:
                raise Exception()
            return cookie
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return
