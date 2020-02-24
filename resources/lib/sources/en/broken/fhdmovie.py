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

from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watchhdmovie.net']
        self.base_link = 'https://watchhdmovie.net'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url == None: return
            urldata = urlparse.parse_qs(url)
            urldata = dict((i, urldata[i][0]) for i in urldata)
            title = urldata['title'].replace(':', ' ').lower()
            year = urldata['year']

            start_url = urlparse.urljoin(self.base_link, self.search_link % (urllib.quote_plus(title)))

            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
            html = self.scraper.get(start_url, headers=headers).content
            r = client.parseDOM(html, 'div', attrs={'class': 'col-lg-8'})[0]
            Links = re.compile('(?s)<a\s*href="([^"]+)"\s*title="([^"]+)"', re.DOTALL).findall(r)
            for link, name in Links:
                link = link.replace('\\', '')
                if cleantitle.get(title) == cleantitle.get(name.split('(' + year, 1)[0]):
                    if year in name:
                        holder = self.scraper.get(link, headers=headers).content
                        src_list1 = re.compile('<button class[^<>]+value="([^"]+)"', re.DOTALL).findall(holder)
                        src_list2 = re.compile('a class="text-capitalize dropdown-item"[^<>]+href="([^"]+)"', re.DOTALL).findall(holder)
                        source_list = src_list1 + src_list2
                        for url in source_list:
                            try:
                                url = 'http' + url.rsplit('http', 1)[-1]
                                if any(x in url for x in ['openload', 'oload', 'uptobox', 'userscloud', '1fichier', 'turbobit', 'ok.ru', 'mail.ru']): quality = '1080p'
                                elif any(x in url for x in ['streamango', 'streamcherry', 'rapidvideo']): quality = '720p'
                                else: quality = 'SD'
                                valid, host = source_utils.is_host_valid(url, hostprDict)
                                if valid: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': [], 'direct': False, 'debridonly': True})
                                else:
                                    valid, host = source_utils.is_host_valid(url, hostDict)
                                    if valid: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': [], 'direct': False, 'debridonly': False})
                            except:
                                pass
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
