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


import re, base64, urllib, urlparse, json, traceback

from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['mydownloadtube.com', 'mydownloadtube.to']
        self.base_link = 'https://www1.mydownloadtube.com'
        self.search_link = '/search/search_val?language=English%20-%20UK&term='
        self.scraper = cfscrape.create_scraper()
        self.useragent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = urllib.quote_plus(title)
            query = urlparse.urljoin(self.base_link, self.search_link + t)
            headers = {'User-Agent': self.useragent}
            r = self.scraper.get(query, headers=headers).content
            result = json.loads(r)

            result = [i for i in result if cleantitle.get(re.sub('\(\d{4}\)', '', i['value'])) == cleantitle.get(title)]
            result = [i for i in result if i['category'] == 'Movies']

            return (result[0]['url'], year)
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url[0] == None: return sources

            headers = {'User-Agent': self.useragent}
            r = self.scraper.get(url[0], headers=headers).content
            yr = re.findall('(?s)m-date>\s*[^<>]+(\d{4})\s*<', r)[0]
            if not yr == url[1]: return sources
            mov_id = re.findall('id=movie value=(.+?)/>', r)[0]
            mov_id = mov_id.rstrip()
            headers = {'Origin': self.base_link, 'Referer': url[0], 'X-Requested-With': 'XMLHttpRequest', 'User-Agent': self.useragent}
            request_url = '%s/movies/play_online' % self.base_link
            form_data = {'movie': mov_id}
            links_page = self.scraper.post(request_url, headers=headers, data=form_data).content
            matches = re.findall("sources:(.+?)controlbar", links_page)
            match = re.findall("file:window.atob.+?'(.+?)'.+?label:\"(.+?)\"", str(matches))

            for link, quality in match:
                try:
                    vid_url = base64.b64decode(link).replace(' ', '%20')
                    quality = quality.replace('3Dp', '3D').replace(' HD', '')
                    sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': vid_url, 'info': '', 'direct': True, 'debridonly': False})
                except:
                    pass

            match2 = re.findall('<[iI][fF][rR][aA][mM][eE].+?[sS][rR][cC]="(.+?)"', links_page)

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for link in match2:
                try:
                    host = link.split('//')[1].replace('www.', '')
                    host = host.split('/')[0].split('.')[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    if '1080' in link: quality = '1080p'
                    elif '720' in link: quality = '720p'
                    else: quality = 'SD'
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': '', 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            url = client.request(url, output='geturl')
            return url
        except:
            return
