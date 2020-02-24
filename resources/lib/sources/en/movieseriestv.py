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
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['movieseriestv.net']
        self.base_link = 'http://www.movieseriestv.net'
        self.search_link = '/?s=%s'


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return tvshowtitle


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

            tvshowtitle = url
            hdlr = 'S%02dE%02d' % (int(season), int(episode))

            t = '%s %s' % (cleantitle.getsearch(tvshowtitle), hdlr)
            query = urlparse.urljoin(self.base_link, self.search_link % t.replace(' ', '+'))
            r = client.request(query)

            result = client.parseDOM(r, 'div', attrs={'class': 'article'})
            result = [(client.parseDOM(i, 'a', ret='title')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(tvshowtitle) == cleantitle.get(i[0].split(hdlr, 1)[0].strip().encode('utf-8')) and hdlr in i[0]]
            if len(result) == 0: raise Exception()

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
			
            link_page = re.findall('a href="([^"]+\.links\.movieseriestv[^"]+)"', r)[0]
            headers = {'Referer': url}

            r1 = client.request(link_page, headers=headers)
                  
            items = client.parseDOM(r1, 'div', attrs={'class': 'tab_content'})[0]
            items = client.parseDOM(items, 'a', ret='href')

            for item in items:
                try:
                    if any(x in item for x in ['.rar', '.zip', '.iso']): raise Exception()
                    if '1080' in item or '.1p' in item: quality = '1080p'
                    elif '720' in item or '.7p' in item: quality = '720p'
                    else: quality = 'SD'
                    valid, hoster = source_utils.is_host_valid(item, hostprDict)
                    urls, host, direct = source_utils.check_directstreams(item, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': True})
                    else:
                        valid, hoster = source_utils.is_host_valid(item, hostDict)
                        urls, host, direct = source_utils.check_directstreams(item, hoster)
                        if valid:
                            for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
