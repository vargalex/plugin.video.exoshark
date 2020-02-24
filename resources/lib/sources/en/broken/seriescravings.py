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

import re
from resources.lib.modules import directstream
from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.base_link = 'http://series-craving.me'


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return tvshowtitle


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

            sxex = 'season-%s-episode-%s' % (season, episode)
            t = cleantitle.getsearch(url)
            urlr = self.base_link + '/watch-%s-online' % t.replace(' ', '-')
            r = client.request(urlr)
            result = client.parseDOM(r, 'div', attrs={'class': 'entry-content'})[0]
            result = client.parseDOM(result, 'li')
            result = [client.parseDOM(i, 'a', ret='href')[0] for i in result]
            result = [i for i in result if sxex in i]

            return result[0]
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            r = client.request(url)
            result = client.parseDOM(r, 'div', attrs={'class': 'entry-content'})[0]
            items = re.findall('<iframe.+?src="([^"]+)"', result)

            for i in items:
                try:
                    if 'google' in i:
                        sources.append({'source': 'GVIDEO', 'quality': 'SD', 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
                    else:
                        valid, hoster = source_utils.is_host_valid(i, hostDict)
                        urls, host, direct = source_utils.check_directstreams(i, hoster)
                        if valid:
                            for x in urls: sources.append({'source': host, 'quality': x['quality'], 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        if 'google' in url:
            return directstream.googlepass(url)
        else:
            return url
