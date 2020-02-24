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


import re,json,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watch32hd.co']
        self.base_link = 'https://watch32hd.co'
        self.search_link = '/watch?v=%s_%s'


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
            title = data['title'] ; year = data['year']

            query = urlparse.urljoin(self.base_link, self.search_link % (cleantitle.getsearch(title).replace(' ', '_'), year))

            c = client.request(query)
            urlr = re.findall('var frame_url = "([^"]+)"', c)[0]
            if not urlr.startswith('http'): urlr = 'http:' + urlr

            result = client.request(urlr)
            urlt = re.findall('var url = \'([^\']+)\'', result)[0]
            urlt = 'http://%s%s' % (urlparse.urlparse(urlr.strip()).netloc, urlt)
			
            r = client.request(urlt)
            result = json.loads(r)

            for i in result:
                try: 
                    # info = []
                    # fsize = i['size']
                    # if fsize.isdigit():
                        # size = int(fsize) 
                        # size = '[B][%.2f GB][/B]' % (size / float(1024 ** 3))
                        # info.append(size)
                    try:
                        quality = directstream.googletag(i)[0]['quality']
                    except:
                        quality = 'SD'
                    sources.append({'source': 'gvideo', 'quality': quality, 'language': 'en', 'url': i['url'], 'direct': True, 'debridonly': False})
                except: pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url
