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

import re,urllib,urlparse, traceback

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['http://supremacy.org.uk']
        self.base_link = 'http://supremacy.org.uk'
        self.indexlist = ['/tombraider/dogsbollocks/0-1000000.txt',
                          '/tombraider/dogsbollocks/A-D.txt',
                          '/tombraider/dogsbollocks/E-H.txt',
                          '/tombraider/dogsbollocks/I-L.txt',
                          '/tombraider/dogsbollocks/M-P.txt',
                          '/tombraider/dogsbollocks/Q-S.txt',
                          '/tombraider/dogsbollocks/T.txt',
                          '/tombraider/dogsbollocks/U-Z.txt']


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
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

            title, year = data['title'], data['year']

            if title[0] in '0123456789':
                url = urlparse.urljoin(self.base_link, self.indexlist[0])
            elif title[0] in 'ABCD':
                url = urlparse.urljoin(self.base_link, self.indexlist[1])
            elif title[0] in 'EFGH':
                url = urlparse.urljoin(self.base_link, self.indexlist[2])
            elif title[0] in 'IJKL':
                url = urlparse.urljoin(self.base_link, self.indexlist[3])
            elif title[0] in 'MNOP':
                url = urlparse.urljoin(self.base_link, self.indexlist[4])
            elif title[0] in 'QRS':
                url = urlparse.urljoin(self.base_link, self.indexlist[5])
            elif title[0] in 'T':
                url = urlparse.urljoin(self.base_link, self.indexlist[6])
            elif title[0] in 'UVWXYZ':
                url = urlparse.urljoin(self.base_link, self.indexlist[7])
            else:
                return sources

            r = client.request(url)
            result = client.parseDOM(r, 'item')
            result = [(client.parseDOM(i, 'title')[0], client.parseDOM(i, 'link')[0]) for i in result]

            links = []

            for i in result:
                try:
                    name = i[0]
                    t = re.sub('(\[[^\[\]]+\])', '', name)
                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d+|3D)(\.|\)|\]|\s|)(.+|)', '', t)

                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()
                    y = re.findall('[\.|\(|\[|\s](\d{4}|(?:S|s)\d*(?:E|e)\d*|(?:S|s)\d*)[\.|\)|\]|\s]', name)[-1].upper()
                    if not y == year: raise Exception()
                    links += [i[1]]
                except:
                    pass

            if len(links) == 0: raise Exception()
            items = '\n'.join(links)
            items = re.findall('LISTSOURCE:(http(?:s|):[^:]+).+?]([^\[\]]+)', items)

            for item in items:
                try:
                    url = item[0]
                    if 'youtube.com' in url: raise Exception()
                    if '1080p' in item[1].lower():
                        quality = '1080p'
                    elif 'hd' in item[1].lower() or '720p' in item[1].lower():
                        quality = '720p'
                    else:
                        quality = 'SD'
                    valid, hoster = source_utils.is_host_valid(url, hostDict)
                    urls, host, direct = source_utils.check_directstreams(url, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                    else:
                        valid, hoster = source_utils.is_host_valid(url, hostprDict)
                        urls, host, direct = source_utils.check_directstreams(url, hoster)
                        if valid:
                            for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': True})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
