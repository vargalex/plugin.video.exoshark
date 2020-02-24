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
        self.domains = ['iwannawatch.is']
        self.base_link = 'https://www.iwannawatch.is'
        self.search_link = '/wp-admin/admin-ajax.php?action=bunyad_live_search&query=%s+%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % (urllib.quote_plus(title), year))
            result = client.request(query)

            result = client.parseDOM(result, 'div', attrs={'class': 'content'})
            if len(result) == 0: raise Exception()

            result = [(client.parseDOM(i, 'a')[0], client.parseDOM(i, 'a', ret = 'href')[0]) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].rsplit('(%s' % year, 1)[0].strip().encode('utf-8')) and year in i[0]]
            if not len(result) == 1: raise Exception()

            return result[0]
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            r = client.request(url)

            items = re.findall('<a.+?data-target="[^"]+host\d{1,2}"\s*data-href="([^"]+)"', r)

            items2 = re.findall('<td class="host".+?<a href="([^"]+)".+?<td class="quality">([^<>]+)<', r)

            for item in items:
                try:
                    valid, hoster = source_utils.is_host_valid(item, hostDict)
                    urls, host, direct = source_utils.check_directstreams(item, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            if items2:
                for itemr in items2:
                    try:
                        q = itemr[1].lower().strip()
                        if q == 'hd': quality = '720p'
                        elif 'cam' in q or 'hdts' in q: quality = 'CAM'
                        else: quality = 'SD'
                        valid, hoster = source_utils.is_host_valid(itemr[0], hostDict)
                        urls, host, direct = source_utils.check_directstreams(itemr[0], hoster)
                        if valid:
                            if quality == '720p':
                                if not any(x in host for x in ['openload', 'streamango', 'streamcherry']): quality = 'SD'
                            for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                    except:
                        pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
