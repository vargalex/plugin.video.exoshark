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

import re,urllib,urlparse,json,traceback

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['123movieshub.re']
        self.base_link = 'https://123movieshub.re'
        self.search_link = '/movie/search/%s'
        self.useragent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'


    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def searchShow(self, title, season, aliases, headers):
        try:
            t = cleantitle.getsearch(title)
            query = urlparse.urljoin(self.base_link, self.search_link % t.replace(' ', '+'))
            r = client.request(query)
            results = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            results = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], re.findall('\-\s*Season\s*(\d+)', i)[0]) for i in results]
            try:
                url = [i[0] for i in results if self.matchAlias(i[1].rsplit(' - Season')[0], aliases) and (season == i[2])][0]
            except:
                url = None
                pass

            if (url == None):
                url = [i[0] for i in results if self.matchAlias(i[1].rsplit(' - Season')[0], aliases)][0]
            return url
        except:
            log_utils.log('>>>> %s HIBA <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGNOTICE)
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            t = cleantitle.getsearch(title)
            query = urlparse.urljoin(self.base_link, self.search_link % t.replace(' ', '+'))
            headers = {'User-Agent': self.useragent}
            r = client.request(query, headers=headers)
            results = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            results = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], re.findall('\(\s*(\d{4})\s*\)', i)[0]) for i in results]
            try:
                url = [i[0] for i in results if self.matchAlias(i[1].rsplit('(')[0], aliases) and (year == i[2])][0]
            except:
                url = None
                pass

            if (url == None):
                url = [i[0] for i in results if self.matchAlias(i[1].rsplit('(')[0], aliases)][0]
            return url
        except:
            log_utils.log('>>>> %s HIBA <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGNOTICE)
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            headers = {}

            if 'tvshowtitle' in data:
                episode = int(data['episode'])
                url = self.searchShow(data['tvshowtitle'], data['season'], aliases, headers)
            else:
                episode = 0
                url = self.searchMovie(data['title'], data['year'], aliases, headers)

            try:
                url = url.rsplit('.', 1)[0] + '/watching.html'
                headers = {'User-Agent': self.useragent}
                r = client.request(url, headers=headers)
                
                if 'tvshowtitle' in data:
                    episodes = client.parseDOM(r, 'div', attrs = {'id': 'list-eps'})[0]
                    episodes = re.findall('href="([^"]+)"[^<>]+>([^<>]+)<\/a>', episodes)
                    content_id = [i[0].rsplit('episode_id=')[-1] for i in episodes if i[1].lower().strip() == 'episode %s' % episode]
                
                else:
                    r1 = client.parseDOM(r, 'div', attrs = {'class': 'modal fade modal-report'})[0]
                    content_id = re.findall('<input type="hidden" name="episode_id" value="([^"]+)"', r1)[0]
                url = self.base_link + '/ajax/v3_get_sources?s=ptserver&id=%s' % content_id
                r = client.request(url, headers=headers)

                result = json.loads(r)
                url = result['value']
                if not url.startswith('http'): url = 'http:' + url
                headers = {'accept': 'application/json, text/javascript, */*; q=0.01', 'origin': self.base_link}
                result = client.request(url, headers=headers)

                results = json.loads(result)
                items = results['playlist'][0]['sources']

                for i in items:
                    try:
                        url = i['file']
                        if not url.startswith('http'): url = 'http:' + url
                        q = i['label']
                        if 'HD' in q or '720p' in q: quality = '720p'
                        elif '1080p' in quality: quality = '1080p'
                        else: quality = 'SD'
                        if 'cdninstagram' in url:
                            sources.append({'source': 'CDN', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
                        elif 'google' in url:
                            sources.append({'source': 'GVIDEO', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
                        else:
                            valid, hoster = source_utils.is_host_valid(url, hostDict)
                            urls, host, direct = source_utils.check_directstreams(url, hoster)
                            if valid:
                                for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                    except:
                        pass

            except:
                pass

            return sources
        except:
            log_utils.log('>>>> %s HIBA <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGNOTICE)
            return sources


    def resolve(self, url):
        return url

        