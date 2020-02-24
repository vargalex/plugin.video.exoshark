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
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['online-filmek.site', 'onlinepont-online.cc', 'onlinefilmpont.site']
        self.base_link = 'https://online-filmek.site'
        self.search_link = '/wp-json/keremiya/search/?keyword=%s&nonce=%s'


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

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            localtitle = data['localtvshowtitle'] if 'localtvshowtitle' in data else data['localtitle']
            year = data['year']

            r = client.request(self.base_link)
            result = re.findall('var sL10n\s*=\s*([^;]+)', r)[0]
            result = json.loads(result)
            nonce = result['nonce'].encode('utf-8')

            query = urlparse.urljoin(self.base_link, self.search_link % (urllib.quote(localtitle), nonce))
            r = client.request(query)

            result = json.loads(r)
            result = result.items()
            result = [i[1] for i in result if cleantitle.get(i[1]['title'].encode('utf-8')) == cleantitle.get(localtitle)]
            result = [i for i in result if i['extra']['date'].encode('utf-8') == year]

            if len(result) == 0: raise Exception()

            url = result[0]['url'].encode('utf-8')

            r = client.request(url)
            tag = client.parseDOM(r, 'div', attrs = {'class': 'video-container'})
            tag = client.parseDOM(tag, 'p')[-1].lower()

            url = client.parseDOM(r, 'div', attrs = {'class': 'single-content tabs'})
            url = client.parseDOM(url, 'a', ret='href')[0]
            url = url.encode('utf-8')

            post = urllib.urlencode({'passster_password': 'onlinepont', 'submit': ''})
            r = client.request(url, post=post)

            result = client.parseDOM(r, 'a', ret = 'href')
            result += client.parseDOM(r.lower(), 'iframe', ret='src')
            result = [i for i in result if not 'youtube.com' in i]
            if not result: raise Exception()

            info = '' if 'feliratos' in tag else 'szinkron'
            quality = 'CAM' if ('cam' in tag or 'mozis' in tag or u'kamer\u00E1s' in tag) else 'SD'

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    host = re.search('(?:\/\/|\.)([^www][\w]+[.][\w]+)\/', item).group(1)
                    host = host.strip().lower().split('.', 1)[0]
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = item.encode('utf-8')
                    if quality == 'SD': quality = source_utils.check_sd_url(url)
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
