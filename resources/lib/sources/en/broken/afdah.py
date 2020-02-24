# -*- coding: utf-8 -*-

'''
    Covenant Add-on

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


import re, json, urllib, urlparse, base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['afdah.info', 'afdah.to']
        self.base_link = 'https://afdah.info'
        self.search_link = '/wp-content/themes/afdah/ajax-search2.php'
        self.goog_link = 'https://www.google.com/search?q=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_url = self.goog_link % urllib.quote_plus('%s %s site:%s' % (title, year, self.base_link))
            r = client.request(search_url)
            result = client.parseDOM(r, 'div', {'class': 'rc'})
            result = [(client.parseDOM(i, 'a')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].split('(' + year, 1)[0].strip().encode('utf-8')) and year in i[0]]
            if len(result) == 0: raise Exception()
            url = client.parseDOM(result, 'a', ret='href')[0]
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources
            surl = []
            r = client.request(url, redirect=True)
            data = client.parseDOM(r, 'div', attrs={'class': 'jw-player'}, ret='data-id')
            data2 = client.parseDOM(r, 'tr')
            data2 = [client.parseDOM(i, 'a', ret='href') for i in data2]
            surl += [i[0] for i in data2 if i]
            surl += [urlparse.urljoin(self.base_link,i) for i in data if not 'trailer' in i]

            for url in surl:
                try:
                    if self.base_link in url:
                        txt = client.request(url)

                        try:
                            code = re.findall(r'decrypt\("([^"]+)', txt)[0]
                            decode = base64.b64decode(tor(base64.b64decode(code)))

                            urls = [(i[0], i[1]) for i in re.findall(
                                '''file\s*:\s*["']([^"']+)['"].+?label\s*:\s*["'](\d+)p["']''', str(decode), re.DOTALL)
                                    if int(i[1]) >= 720]
                            for i in urls:
                                url = i[0]
                                quality = i[1] + 'p'
                                sources.append(
                                    {'source': 'GVIDEO', 'quality': quality, 'language': 'en', 'url': url,
                                     'direct': True,
                                     'debridonly': False})
                        except:
                            code = re.findall(r'salt\("([^"]+)', txt)[0]
                            decode = tor(base64.b64decode(tor(code)))
                            url = client.parseDOM(str(decode), 'iframe', ret='src')[0]
                            sources.append(
                                {'source': 'NETU', 'quality': '1080p', 'language': 'en', 'url': url, 'direct': False,
                                 'debridonly': False})

                except:
                    pass
                try:
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if not valid: continue
                    sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                except: pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url


def tor(txt):
    try:
        map = {}
        tmp = "abcdefghijklmnopqrstuvwxyz"
        buf = ""
        j = 0;
        for c in tmp:
            x = tmp[j]
            y = tmp[(j + 13) % 26]
            map[x] = y;
            map[x.upper()] = y.upper()
            j += 1

        j = 0
        for c in txt:
            c = txt[j]
            if c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z':
                buf += map[c]
            else:
                buf += c
            j += 1

        return buf
    except:
        return
