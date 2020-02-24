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

import re, urlparse, urllib

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['vodly.us', 'vodly.unblocked.pro']
        self.base_link = 'http://vodly.us'
        self.search_link = '/search?s=%s'
        self.goog_link = 'https://www.google.com/search?q=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_url = self.goog_link % urllib.quote_plus('%s %s site:%s' % (title, year, self.base_link))
            r = client.request(search_url)
            result = client.parseDOM(r, 'div', {'class': 'rc'})
            result = [(client.parseDOM(i, 'a')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].replace('Watch', '').split(year, 1)[0].strip().encode('utf-8')) and year in i[0]]
            if len(result) == 0: raise Exception()
            url = client.parseDOM(result, 'a', ret='href')[0]
            url = url.encode('utf-8')
            return url
        except Exception:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = cache.get(client.request, 1, url)
            try:
                v = client.parseDOM(r, 'iframe', ret='data-src')[0]

                url = v.split('=')[1]
                try:
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({
                        'source': host,
                        'quality': 'SD',
                        'language': 'en',
                        'url': url.replace('\/', '/'),
                        'direct': False,
                        'debridonly': False
                    })
                except:
                    pass
            except:
                pass
            r = client.parseDOM(r, 'tbody')
            r = client.parseDOM(r, 'tr')
            r = [(re.findall('<td>(.+?)</td>', i)[0], client.parseDOM(i, 'a', ret='href')[0]) for i in r]

            if r:
                for i in r:
                    try:
                        host = i[0]
                        url = urlparse.urljoin(self.base_link, i[1])
                        host = host.replace('www.', '')
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        if 'other'in host: continue
                        sources.append({
                            'source': host,
                            'quality': 'SD',
                            'language': 'en',
                            'url': url.replace('\/', '/'),
                            'direct': False,
                            'debridonly': False
                        })
                    except:
                        pass
            return sources
        except Exception:
            return


    def resolve(self, url):
        if self.base_link in url:
            url = client.request(url)
            url = client.parseDOM(url, 'div', attrs={'class': 'wrap'})
            url = client.parseDOM(url, 'a', ret='href')[0]
        return url
