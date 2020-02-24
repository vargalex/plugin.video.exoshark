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
from resources.lib.modules import source_utils
from resources.lib.modules import cfscrape
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['extramovies.wiki', 'extramovies.host', 'extramovies.trade', 'extramovies.cc']
        self.base_link = 'http://extramovies.wiki'
        self.search_link = '/?s=%s+%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = cleantitle.getsearch(title)
            search_url = urlparse.urljoin(self.base_link, self.search_link % (t.replace(' ', '+'), year))
            r = client.request(search_url)
            result = client.parseDOM(r, 'div', attrs={'id': 'content'})[0]
            result = client.parseDOM(result, 'div', attrs={'class': 'imag'})
            result = [(client.parseDOM(i, 'a', ret='title')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].split(year, 1)[0].replace('(', '').strip().encode('utf-8')) and year in i[0]]
            if len(result) == 0: raise Exception()
            result = [(client.parseDOM(i, 'div', attrs={'class': 'mylanguage'})[0], i) for i in result]
            result = [i[1] for i in result if 'english' in i[0].lower()]
            url = client.parseDOM(result, 'a', ret='href')[0]
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            r = client.request(url)

            qual = re.findall('(?:Q|q)uality:\s*<\/b>(.+?)\s*(?:S|s)ize', r)[0]
            qual = re.sub('<.+?>', '', qual)
            if '1080p' in qual.lower(): quality = '1080p'
            elif '720p' in qual.lower(): quality = '720p'
            else: quality = 'SD'

            r1 = client.parseDOM(r, 'h4')
            items = client.parseDOM(r1, 'a', ret='href')

            for item in items:
                try:
                    if item.startswith('/download.php'):
                        url = item.rsplit('link=', 1)[-1].rsplit('&#038', 1)[0]
                        try: url = url.decode('base64')
                        except: pass
                        if 'multiup' in url:
                            urlr = url.replace('.org', '.eu').replace('/download/', '/en/mirror/')
                            rr = self.scraper.get(urlr).content
                            result = client.parseDOM(rr, 'div', attrs={'class': 'col-md-4'})
                            result = client.parseDOM(result, 'a', ret='href')
                            for i in result:
                                valid, hoster = source_utils.is_host_valid(i, hostprDict)
                                urls, host, direct = source_utils.check_directstreams(i, hoster)
                                if valid:
                                    for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': True})
                        valid, hoster = source_utils.is_host_valid(url, hostprDict)
                        urls, host, direct = source_utils.check_directstreams(url, hoster)
                        if valid:
                            for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': True})
                    elif item.startswith('/video.php'):
                        url = urlparse.urljoin(self.base_link, item)
                        sources.append({'source': 'GVIDEO', 'quality': 'SD', 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
                    else:
                        url = urlparse.urljoin(self.base_link, item)
                        host = item.split('.php', 1)[0].replace('/', '').strip()
                        valid, hoster = source_utils.is_host_valid(host, hostDict)
                        urls, host, direct = source_utils.check_directstreams(host, hoster)
                        if valid:
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            if self.base_link in url:
                r = client.request(url)
                try: url = client.parseDOM(r, 'iframe', ret='src')[0]
                except: url = client.parseDOM(r, 'IFRAME', ret='SRC')[0]
                if url.startswith('/player/video.php'):
                    urlr = urlparse.urljoin(self.base_link, url)
                    r1 = client.request(urlr)
                    url = re.findall('{file:\s*"([^"]+)"', r1)[0]
                    url = url.encode('utf-8')
                return url
            else:
                return url
        except:
            return
