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
        self.domains = ['hdmoviesdownload.com']
        self.base_link = 'http://hdmoviesdownload.com'
        self.search_link = '/?s=%s+%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = title + ' ' + year
            titl = re.sub('(\\\|/|-|:|;|,|\.|\*|\?|"|\'|<|>|\|)', '', title)

            query = urlparse.urljoin(self.base_link, self.search_link % (urllib.quote_plus(titl), year))
            r = client.request(query)

            result = client.parseDOM(r, 'main', attrs={'class': 'content'})[0]
            result = client.parseDOM(result, 'article')
            result = [(client.parseDOM(i, 'a')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(t) in cleantitle.get(i[0])]
            if not len(result) == 1: raise Exception()

            url = client.parseDOM(result, 'a', ret='href')[0]
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            r = client.request(url)
            info = []
            fsize = re.search('(?:m|M)ovie (?:s|S)ize\s*:\s*([^<>]+)\s*', r).group(1)
            if fsize != None: 
                fs = '[B][%s][/B]' % fsize
                info.append(fs)
            fqual = re.search('(?:m|M)ovie (?:q|Q)uality\s*:\s*([^<>]+)\s*', r).group(1)
            if '1080p' in fqual.lower(): quality = '1080p'
            elif '720p' in fqual.lower(): quality = '720p'
            elif 'cam' in fqual.lower() or 'ts' in fqual.lower(): quality = 'CAM'
            else: quality = 'SD'
            fqual_upd = client.parseDOM(r, 'h1', attrs={'class': 'entry-title'})[0]
            if 'cam' in fqual_upd.lower(): quality = 'CAM'

            postdata = re.search('(?s)<form action="([^"]+)".+?<input name="FileName" type="hidden" value="([^"]+)".+?<input name="FileSize" type="hidden" value="([^"]+)".+?<input name="FilseServer" type="hidden" value="([^"]+)"', r)
            query = postdata.group(1); postfn = postdata.group(2); postfs = postdata.group(3); postsr = postdata.group(4)
            if 'hdpopcorns' in query: raise Exception()
            post = urllib.urlencode({'FileName': postfn, 'FileSize': postfs, 'FilseServer': postsr, 'x': '1', 'y': '1'})
            r = client.request(query, post=post)

            result = re.search('<meta http-equiv="refresh" content="([^"]+)"', r).group(1)
            item = result.split('url=')[-1]

            try:
                url = item
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')
                sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'info': ' | '.join(info), 'direct': True, 'debridonly': False})
            except:
                pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url