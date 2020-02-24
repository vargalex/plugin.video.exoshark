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
        self.domains = ['www.onlinefilmekingyen.com']
        self.base_link = 'https://www.onlinefilmekingyen.com'
        self.search_link = '/kereso/?%s'


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

            query = urllib.urlencode({'search_query': localtitle, 'orderby': '', 'order': '', 'tax_release-year[]': year, 'wpas': '1'})
            query = urlparse.urljoin(self.base_link, self.search_link % query)
            result = client.request(query)

            result = client.parseDOM(result, 'div', attrs={'class': 'datos'})
            if len(result) == 0: raise Exception()
            result = [(client.parseDOM(i, 'a')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]

            if not result: raise Exception()

            url = client.parseDOM(result, 'a', ret = 'href')[0]

            r = client.request(url)

            tag = client.parseDOM(r, 'span', attrs={'class': 'calidad2'})[0]
            tag = tag.lower()

            if 'cam' in tag: quality = 'CAM'
            elif '1080p' in tag: quality = '1080p'
            elif '720p' in tag: quality = 'HD'
            else: quality = 'SD'
            info = []
            if not 'sub' in tag and not 'engdub' in tag: info.append('szinkron')

            result = client.parseDOM(r, 'div', attrs={'id': 'player2'})[0]
            result = result.split('</iframe>')
            if not result: raise Exception()

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    url = re.search('iframe.+?src="([^"]+)"', item).group(1)
                    if url.startswith('/video'):
                        urlr = urlparse.urljoin(self.base_link, url)
                        urlr = client.request(urlr)
                        url = re.search('iframe.+?src="([^"]+)"', urlr).group(1)
                    if url.startswith('//'): url = 'http:' + url
                    if 'sibeol' in url:
                        r = client.request(url)
                        url = re.compile('"?file"?\s*:\s*"([^"]+)"\s*,\s*"?label"?\s*:\s*"(\d+)p?"').findall(r)

                        links = [(i[0], '1080p') for i in url if int(i[1]) >= 1080]
                        links += [(i[0], 'HD') for i in url if 720 <= int(i[1]) < 1080]
                        links += [(i[0], 'SD') for i in url if 480 <= int(i[1]) < 720]

                        for i in links: sources.append({'source': 'gvideo', 'quality': i[1], 'language': 'hu', 'info': ' | '.join(info), 'url': i[0], 'direct': True, 'debridonly': False})
                    else:
                        url = client.replaceHTMLCodes(url)
                        url = url.encode('utf-8')
                        host = re.search('(?:\/\/|\.)([^www][\w]+)[.][\w]+', url).group(1)
                        host = host.strip().lower()
                        host = [x[1] for x in locDict if host == x[0]][0]
                        if not host in hostDict: raise Exception()
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': ' | '.join(info), 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources

    def resolve(self, url):
            return url
