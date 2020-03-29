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
from resources.lib.modules import es_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmezz.eu']
        self.base_link = 'http://filmezz.eu'
        self.search_link = '/livesearch.php?query=%s&type=0'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            for a in [title, localtitle]:
                try:
                    query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(a))
                    r = client.request(query)
                    result = client.parseDOM(r, 'li')
                    result = [(client.parseDOM(i, 'a')[0], i) for i in result]
                    result = [i for i in result if cleantitle.get(title) == cleantitle.get(i[0].encode('utf-8')) or cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
                    result = [i[1] for i in result if re.search('\s*\((\d{4})\)$', i[0]).group(1) == year]
                    if len(result) > 0: break
                except:
                    pass
            if len(result) == 0: raise Exception()

            url = client.parseDOM(result[0], 'a', ret='href')[0]
            return (url, '', imdb)
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

            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote(title))
            r = client.request(query)
            result = r.split('</li>')

            result = [i for i in result if 'film.php?' in i]
            result = [i for i in result if '-%s-evad' % season in i]
            if len(result) == 0: raise Exception()

            url = client.parseDOM(result, 'a', ret='href')[0]
            return (url, episode, imdb)
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            query = urlparse.urljoin(self.base_link, url[0]).encode('utf-8')

            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs={'class': 'sidebar-article details'})[0]
            imdb_id = re.findall('imdb"\s*.+?title\/(.+?)\/', result)[0]
            result = [i for i in result if imdb_id == url[2]]
            if len(result) == 0: raise Exception()

            contentBox = client.parseDOM(r, "section", attrs={'class': 'content-box'})[0]
            href = client.parseDOM(contentBox, 'a', ret="href")[0]

            r = client.request(href)

            items = client.parseDOM(r, 'ul', attrs={'class': 'list-unstyled table-horizontal url-list'})[0]
            items = client.parseDOM(items, 'li')

            if url[1].isdigit():
                items = [i for i in items if '>%s. epiz' % url[1] in i]

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in items:
                try:
                    host = re.search('/ul>([^<]+)', item).group(1)
                    host = host.strip().lower().rsplit('.', 1)[0]
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    l = client.parseDOM(item, 'li', ret='class')[0]
                    info = []
                    if l == 'lhun': info.append('szinkron')
                    q = client.parseDOM(item, 'li', ret='class')[1]
                    if 'qcam' in q: quality = 'CAM'
                    elif 'qhd' in q: quality = 'HD'
                    else: quality = 'SD'
                    url = client.parseDOM(item, 'a', ret='href')[-1]
                    url = 'http' + url.rsplit('http', 1)[-1]
                    url = urllib.unquote(url)
                    url = url.encode('utf-8')
                    
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': ' | '.join(info), 'url': url, 'direct': False, 'debridonly': False, 'sourcecap': True})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            f_domain = urlparse.urlsplit(self.base_link).netloc
            location = client.request(url, output='geturl')

            if f_domain in location:
                cookie = client.request(location, output='cookie', close=False)
                captcha_img = self.base_link + '/captchaimg.php'
                solution = es_utils.captcha_resolve(captcha_img, cookie)
                if solution == '': raise Exception()
                post = urllib.urlencode({'captcha': solution, 'submit': 'Ok'})
                headers = {'Cookie': cookie, 'Referer': url}
                location = client.request(location, output='geturl', post=post, headers=headers) 

            if 'videohuse.' in location:
                r = client.request(location)
                location = client.parseDOM(r, 'iframe', ret='src')[0]

            return location
        except:
            return
