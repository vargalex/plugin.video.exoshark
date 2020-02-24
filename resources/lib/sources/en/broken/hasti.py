# -*- coding: utf-8 -*-

'''
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

import re, urllib, urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['dl.hastidl.me']
        self.base_link = 'http://dl.hastidl.me'
        self.path_link = '/remotes'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

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

            if url is None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            url = urlparse.urljoin(self.base_link, self.path_link)

            r = client.request(url, timeout=5)
            r = re.sub('((?s)<html>.+?a href="trash[^\:]+\:\d+\s*\-)', '', r)
            result = re.compile('<a href="(.+?)">(.+?)<\/a>\s*\d*\-[^-]+\-\d*\s*[\d\:]+\s*(\d*)').findall(r)

            for url, name, fsize in result:
                t = cleantitle.get(name.lower())
                if t.startswith(cleantitle.get(title.lower())):
                    if hdlr.lower() in name.lower() or hdlr.lower() in url.lower():
                        try:
                            url = self.base_link + self.path_link + '/' + url
                            if 'farsi' in url.lower(): raise Exception()
                            if 'trailer' in url.lower() and not url.lower().startswith('trailer'): raise Exception()
                            if any(x in url for x in ['.rar', '.zip', '.iso', '.bin', '.mka', '.jpg']): raise Exception()
                            url = client.replaceHTMLCodes(url)
                            url = url.encode('utf-8')
                            if '1080p' in name.lower(): quality = '1080p'
                            elif '720p' in name.lower(): quality = 'HD'
                            elif 'hdts' in name.lower() or 'hdcam' in name.lower() or 'camrip' in name.lower(): quality = 'CAM'
                            else: quality = 'SD'
                            info = []
                            if fsize.isdigit():
                                size = int(fsize) 
                                size = '%.2f GB' % (size / float(1024 ** 3))
                                info.append(size)
                            sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'info': ' | '.join(info), 'direct': True, 'debridonly': False})
                        except:
                            pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url
