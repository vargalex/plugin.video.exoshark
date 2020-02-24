'''
    Covenant Add-on
    Copyright (C) 2016 Covenant

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
import urllib
import urlparse
import json

from resources.lib.modules import client, cleantitle, directstream

class source:
    def __init__(self):
        '''
        Constructor defines instances variables

        '''
        self.priority = 1
        self.language = ['en']
        self.domains = ['moviesgolds.net']
        self.base_link = 'http://www.moviesgolds.net'
        self.search_path = '/wp-json/dooplay/search/?keyword=%s&nonce=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            r = client.request(self.base_link)
            nonce = re.search('"nonce"\:"([^"]+)"', r).group(1)
            query = urlparse.urljoin(self.base_link, self.search_path % (urllib.quote_plus(title), nonce))

            r = client.request(query)
            json_resub = re.sub('(\{"\d+"\:)', '', r)
            json_resub = re.sub('("\d+"\:)', '', json_resub)
            json_resub = re.sub('}}}', '}}', json_resub)
            json_norm = '[%s]' % json_resub
            result = json.loads(json_norm)

            result = [i for i in result if not 'telugu' in i and not 'hindi' in i and not 'tamil' in i]
            result = [i for i in result if cleantitle.get(i['title'].split('(' + year, 1)[0].strip().encode('utf-8')) == cleantitle.get(title)]
            result = [i for i in result if i['extra']['date'] == year]

            url = result[0]['url'].encode('utf-8')

            response = client.request(url)

            url = re.findall('''<a\s*href=['\"](http://www\.buzzmovie\.site/\?p=\d+)''', response)[0]

            return url
        except Exception:
            return
            
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
                    
            info_response = client.request(url)

            iframes = re.findall('''<iframe\s*src=['"]([^'"]+)''', info_response)

            for url in iframes:
                host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                if host in hostDict:
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({
                        'source': host,
                        'quality': 'SD',
                        'language': 'en',
                        'url': url.replace('\/','/'),
                        'direct': False,
                        'debridonly': False
                    })
            return sources
        except Exception:
            return

    def resolve(self, url):
        return url