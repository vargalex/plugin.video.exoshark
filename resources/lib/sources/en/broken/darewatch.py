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


import re, urlparse, traceback
from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['ondarewatch.com', 'thedarebox.com', 'dailytvfix.com']
        self.base_link = 'http://www.dailytvfix.com'
        self.search_link = '/index.php'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:            
            headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                       'accept-encoding': 'gzip, deflate, br','accept-language':'en-US,en;q=0.8', 'content-type': 'application/x-www-form-urlencoded',
                       'origin': self.base_link, 'referer': self.base_link + '/search'}
            
            post = {'menu': 'search', 'query': title}
            query = urlparse.urljoin(self.base_link, self.search_link)
            html = self.scraper.post(query, headers=headers, data=post).content
            page = html.split('Movie results for:')[1]
            Regex = re.compile('<h4>.+?class="link" href="(.+?)" title="(.+?)"', re.DOTALL).findall(page)
            for url, name in Regex:
                if cleantitle.get(title) == cleantitle.get(name) and '(' + year in name:
                    url = url.encode('utf-8')
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return tvshowtitle


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

            tvshowtitle = url

            headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                       'accept-encoding': 'gzip, deflate, br','accept-language':'en-US,en;q=0.8', 'content-type': 'application/x-www-form-urlencoded',
                       'origin': self.base_link, 'referer': self.base_link + '/search'}
            
            post = {'menu': 'search', 'query': tvshowtitle}

            query = urlparse.urljoin(self.base_link, self.search_link)
            html = self.scraper.post(query, headers=headers, data=post).content
            page = html.split('TV show results for:')[1]
            Regex = re.compile('<h4>.+?class="link" href="(.+?)" title="(.+?)"', re.DOTALL).findall(page)
            for url, name in Regex:
                if cleantitle.get(tvshowtitle) == cleantitle.get(name) and not '/watchm/' in url:
                    url = url + '/season/%s/episode/%s' % (season, episode)
                    url = url.encode('utf-8')
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = self.scraper.post(url).content


            items = re.compile('embeds\[\d*\]\s*=\s*\'([^\']+)\'', re.DOTALL).findall(r)
            items = [i.decode('base64') for i in items]

            for vid in items:
                try:
                    item = re.compile('iframe src="([^"]+)"', re.DOTALL).findall(vid.lower())[0]
                    valid, hoster = source_utils.is_host_valid(item, hostDict)
                    urls, host, direct = source_utils.check_directstreams(item, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': x['quality'], 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
