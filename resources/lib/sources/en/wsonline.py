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
from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import debrid
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['watchseries-online.be']
        self.base_link = 'https://ww1.watchseries-online.be'
        self.scraper = cfscrape.create_scraper()


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
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

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode']))

            url = self.base_link + '/episode/%s' % cleantitle.geturl(query)

            r = self.scraper.get(url).content

            items = re.findall('(?s)tr class="(?:odd|even)">.+?href="([^"]+)', r)
            if items == []: return sources

            for item in items:
                try:
                    url = item.rsplit('?id=')[-1]
                    url = url.decode('base64')
                    valid, hoster = source_utils.is_host_valid(url, hostprDict)
                    urls, host, direct = source_utils.check_directstreams(url, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': True})

                    valid, hoster = source_utils.is_host_valid(url, hostDict)
                    urls, host, direct = source_utils.check_directstreams(url, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
