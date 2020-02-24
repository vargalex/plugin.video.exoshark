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
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cfscrape
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['oakmovies.com', 'ionlinemovies.com']
        self.base_link = 'http://oakmovies.com'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()
        self.useragent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_id = cleantitle.getsearch(title)
            start_url = urlparse.urljoin(self.base_link, self.search_link % search_id.replace(' ', '+'))
            headers = {'User-Agent': self.useragent}
            r = self.scraper.get(start_url, headers=headers).content

            result = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            result = [(re.findall('a href="([^"]+)"', i)[0], client.parseDOM(i, 'h2')[0], re.findall('>\s*(\d{4})\s*<', i)[0]) for i in result]

            url = [i[0] for i in result if cleantitle.get(i[1]) == cleantitle.get(title) and (year == i[2])][0]

            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            items = []
            if url == None: return sources

            html = self.scraper.get(url).content
            source = client.parseDOM(html, 'iframe', ret='src')[0]
            if 'consistent.stream' in source:
                headers = {'Host': 'consistent.stream', 'User-Agent': self.useragent, 'Referer': url}
                r = self.scraper.get(source, headers=headers).content

                video_key, key_hash, exp = re.findall('<player video="([^"]+)" hash="([^"]+)" expire="([^"]+)">', r)[0]
                headers2 = {'Host': 'consistent.stream', 'Origin': 'https://consistent.stream', 'User-Agent': self.useragent,
                            'Content-Type': 'application/json;charset=UTF-8', 'Referer': source}
                payload = {'video': video_key, 'referrer': url, 'key': key_hash, 'expire': exp}

                r2 = self.scraper.post('https://consistent.stream/api/getVideo', headers=headers2, data=json.dumps(payload)).content

                sources_json = json.loads(r2)

                servers = sources_json['servers']
                for i in servers:
                    sources_ = i['sources']
                    for j in sources_:
                        items.append(j['src'])

                for item in items:
                    try:
                        if '1080p' in item: quality = '1080p'
                        elif '720p' in item: quality = '720p'
                        elif '.ts.' in item or 'cam' in item: quality = 'CAM'
                        else: quality = 'SD'
                        valid, host = source_utils.is_host_valid(item, hostDict)
                        if valid:
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': item, 'info': '', 'direct': False, 'debridonly': False})
                        else:
                            if 'consistent.stream/api/cdnVideo' in item:
                                sources.append({'source': 'CDN', 'quality': quality, 'language': 'en', 'url': item, 'info': '', 'direct': True, 'debridonly': False})
                            elif 'uploadhaven.com' in item:
                                sources.append({'source': 'uploadhaven', 'quality': 'SD', 'language': 'en', 'url': item, 'info': '', 'direct': False, 'debridonly': False})  
                    except:
                        pass
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
