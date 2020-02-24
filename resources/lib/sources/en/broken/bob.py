# -*- coding: UTF-8 -*-

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

import re,urllib,urlparse

from resources.lib.modules import client
from resources.lib.modules import cleantitle

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['bobmovies.net']
        self.base_link = 'https://bobmovies.net'

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
            urldata = urlparse.parse_qs(url)
            urldata = dict((i, urldata[i][0]) for i in urldata)
            title = urldata['title']
            year = urldata['year']

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
            post = urllib.urlencode({'do': 'search', 'subaction': 'search', 'story': title})

            r = client.request(self.base_link, post=post, headers=headers)
            result = client.parseDOM(r, 'div', attrs = {'class': 'nnoo short_story'})
            result = [(client.parseDOM(i, 'p')[-1], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            result = [(re.search('>\s*(\d{4})\s*<\/span>', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]
            if not len(result) == 1: raise Exception()

            url = client.parseDOM(result, 'a', ret='href')[0]

            html = client.request(url, headers=headers)
            
            vidpage = re.compile('id="tab-movie".+?data-file="(.+?)"', re.DOTALL).findall(html)

            q = re.search('(?s)<tr>\s*<td class="name">Quality:<\/td>\s*<td>\s*([^<>]+)\s*<\/td>', html).group(1)
            qual = q.lower()
            if qual == 'hd' or qual == 'web-dl': quality = 'HD'
            elif qual == 'hdcam' or qual == 'camrip' or qual == 'ts': quality = 'CAM'
            else: quality = 'SD'

            for link in vidpage:
                if 'trailer' not in link.lower():
                    link = self.base_link + link
                    sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': link, 'info': [], 'direct': True, 'debridonly': False})
            return sources   
        except:
            return sources


    def resolve(self, url):
        return url
